from collections import namedtuple
import time

from minesweeper import Command, CmdType, BoardState


class MineSweeperAI(object):
    NUM_GAMES = 20
    THINK_DELAY = 0.1   # Seconds

    CellRisk = namedtuple('CellRisk', ['risk', 'x', 'y'])

    def __init__(self, game):
        self._game = game
        self._cache = {}

    def __iter__(self):
        return self

    def next(self):
        self._clear_cache()
        time.sleep(self.THINK_DELAY)
        self._game.footer = ''

        if self._game.game_over:
            time.sleep(self.THINK_DELAY)
            if self._game.num_games >= self.NUM_GAMES:
                raise StopIteration()
            else:
                return Command(CmdType.NONE, 0, 0)

        hidden_cells = [(x, y) for x, y, state in self._game.board if state == BoardState.HIDDEN]
        risks = sorted(self._moves(hidden_cells), key=lambda r: r.risk)
        best_reveal = risks[0]
        best_flag = risks[-1]
        if best_flag.risk >= 1.0:
            return Command(CmdType.TOGGLE_FLAG, best_flag.x, best_flag.y)
        else:
            if best_reveal.risk > 0.0:
                self._game.footer = 'GUESS: %s' % best_reveal.risk
            return Command(CmdType.REVEAL, best_reveal.x, best_reveal.y)

    def _moves(self, cells):
        for x, y in cells:
            risk = self._calc_risk(x, y)
            yield risk
            if risk == 0.0 or risk == 1.0:
                return

    def _calc_risk(self, x, y):
        if self._is_definite_safe(x, y):
            return self.CellRisk(0, x, y)

        if self._is_definite_mine(x, y):
            return self.CellRisk(1.0, x, y)

        general_prob = float(self._game.board.num_mines - self._game.num_flags) / \
                       float(self._game.board.num_hidden - self._game.num_flags)

        def prob_mine(ax, ay):
            val = self._game.board.get(ax, ay)
            if val is None:
                # Prefer edges since they have a better chance of revealing more cells.
                return general_prob / 2.0
            if val > 8:
                # No extra information.
                return general_prob

            # Use number of expected versus found mines to estimate likelihood.
            hidden = self._count_neighbours_state(ax, ay, BoardState.HIDDEN)
            flags = self._count_neighbours_state(ax, ay, BoardState.FLAG)
            return float(val - flags) / float(hidden)

        # Calculating actual probability takes exponential time.
        # Let's average probabilities to get a rough estimate of risk.
        probabilities = [prob_mine(ax, ay) for ax, ay in self._game.board._adjacent_pos(x, y)]
        probabilities = [p for p in probabilities if p is not None]
        return self.CellRisk(sum(probabilities) / len(probabilities), x, y)

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

            if state <= 8 and num_hidden_neighbours_of_n <= state - num_flagged_neighbours_of_n:
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
