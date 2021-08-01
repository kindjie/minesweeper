from collections import namedtuple
import time

from minesweeper.minesweeper import Command, CmdType, BoardState


class MineSweeperAI(object):
    NUM_GAMES = 20
    THINK_DELAY = 0.1       # Seconds
    GAME_OVER_DELAY = 1.0   # Seconds

    _MIN_RISK = 0.0
    _MAX_RISK = 1.0
    _NUM_NEIGHBOURS = 8

    CellRisk = namedtuple('CellRisk', ['risk', 'x', 'y'])

    def __init__(self, game):
        self._game = game
        self._cache = {}

    def __iter__(self):
        return self

    def next(self):
        self._clear_cache()
        time.sleep(self.THINK_DELAY)

        if self._game.game_over:
            return self._handle_game_over()

        best_flag_move, best_reveal_move = self._find_best_moves()
        if best_flag_move.risk >= self._MAX_RISK:
            return Command(CmdType.TOGGLE_FLAG, best_flag_move.x, best_flag_move.y)
        else:
            # Might need to guess if we aren't certain about a flag.
            return Command(CmdType.REVEAL, best_reveal_move.x, best_reveal_move.y)

    __next__ = next

    def _moves(self, cells):
        for x, y in cells:
            risk = self._calc_risk(x, y)
            yield risk
            if risk == self._MIN_RISK or risk == self._MAX_RISK:
                # Found candidate move, so we can stop.
                return

    def _find_best_moves(self):
        hidden_cells = [(x, y) for x, y, state in self._game.board if state == BoardState.HIDDEN]
        risks = sorted(self._moves(hidden_cells), key=lambda r: r.risk)
        best_reveal = risks[0]
        best_flag = risks[-1]
        return best_flag, best_reveal

    def _calc_risk(self, x, y):
        if self._is_definite_safe(x, y):
            return self.CellRisk(self._MIN_RISK, x, y)

        if self._is_definite_mine(x, y):
            return self.CellRisk(self._MAX_RISK, x, y)

        general_prob = float(self._game.board.num_mines - self._game.num_flags) / \
                       float(self._game.board.num_hidden - self._game.num_flags)

        def prob_mine(ax, ay):
            val = self._game.board.get(ax, ay)
            if val is None:
                # Prefer edges since they have a better chance of revealing more cells.
                return general_prob / 2.0
            if val > self._NUM_NEIGHBOURS:
                # No extra information from this cell.
                return general_prob

            # Use number of expected versus found mines to estimate likelihood.
            hidden = self._count_neighbours_state(ax, ay, BoardState.HIDDEN)
            flags = self._count_neighbours_state(ax, ay, BoardState.FLAG)
            return float(val - flags) / float(hidden)

        # Calculating actual probability takes exponential time.
        # Let's average probabilities to get a rough estimate of risk.
        probabilities = [prob_mine(ax, ay) for ax, ay in self._game.board._adjacent_pos(x, y)]
        return self.CellRisk(sum(probabilities) / len(probabilities), x, y)

    def _handle_game_over(self):
        time.sleep(self.GAME_OVER_DELAY)
        if self._game.num_games >= self.NUM_GAMES:
            raise StopIteration()
        else:
            return Command(CmdType.NONE, 0, 0)

    def _count_neighbours_state(self, x, y, state):
        if not self._in_cache('count', (x, y, state)):
            self._set_cache('count', (x, y, state),
                            sum(1 for ax, ay in self._game.board._adjacent_pos(x, y) \
                                if self._game.board.get(ax, ay) == state))
        return self._get_cache('count', (x, y, state))

    def _get_neighbour_values(self, x, y):
        return [self._game.board.get(ax, ay) for ax, ay in self._game.board._adjacent_pos(x, y)]

    def _is_definite_safe(self, x, y):
        return any(self._count_neighbours_state(ax, ay, BoardState.FLAG) == \
                   self._game.board.get(ax, ay) for ax, ay in self._game.board._adjacent_pos(x, y))

    def _is_definite_mine(self, x, y):
        neighbours = self._game.board._adjacent_pos(x, y)
        for n in neighbours:
            num_flagged_neighbours_of_n = self._count_neighbours_state(*n, state=BoardState.FLAG)
            num_hidden_neighbours_of_n = self._count_neighbours_state(*n, state=BoardState.HIDDEN)

            state = self._game.board.get(*n)
            if state is None:
                continue

            if state <= self._NUM_NEIGHBOURS and num_hidden_neighbours_of_n <= \
                                                 state - num_flagged_neighbours_of_n:
                return True
        return False

    def _set_cache(self, method, params, value):
        self._cache[(method, params)] = value

    def _in_cache(self, method, params):
        return (method, params) in self._cache

    def _get_cache(self, method, params):
        return self._cache[(method, params)]

    def _clear_cache(self):
        self._cache = {}
