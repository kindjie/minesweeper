from unittest import TestCase

from minesweeper.game import State
from minesweeper.minesweeper import (MineSweeper, BoardState, Command, map_cell_state_to_renderable,
                         CmdType, Strings)
from minesweeper.minesweeper_cli import map_key_to_command, CmdKey


def assert_attributes_equal(test_case, obj_a, obj_b, attributes):
    test_case.assertEquals([(a, getattr(obj_b, a)) for a in attributes],
                           [(a, getattr(obj_a, a)) for a in attributes])


class TestMineSweeper(TestCase):
    VALIDATE_ATTR = ['title', 'footer', 'message', '_state', '_cursor_pos', '_num_flags',
                     '_num_mines_flagged', '_start_time']

    def setUp(self):
        self.ms = self._create_default_game()

    @staticmethod
    def _create_default_game():
        ms = MineSweeper(4, 4, 1)
        ms.board.create_mines()
        return ms

    def _create_arbitrary_game(self):
        ms = self._create_default_game()
        for p in self.VALIDATE_ATTR:
            setattr(ms, p, 'Arbitrary value')
        return ms

    def test_cursor_pos_new_game_returns_origin(self):
        pos = self.ms.cursor_pos
        self.assertEquals((0, 0), pos)

    def test_board_new_game_returns_all_hidden(self):
        board = self.ms.board
        self.assertTrue(all(state == BoardState.HIDDEN for _, _, state in board))

    def test_game_over_new_game_returns_false(self):
        game_over = self.ms.game_over
        self.assertFalse(game_over)

    def test_game_over_victory_game_returns_true(self):
        self.ms._end(True)
        game_over = self.ms.game_over
        self.assertTrue(game_over)

    def test_game_over_defeat_game_returns_true(self):
        self.ms._end(False)
        game_over = self.ms.game_over
        self.assertTrue(game_over)

    def test_game_state_new_game_returns_starting(self):
        _, _, state = self.ms.game_state
        self.assertEquals(State.STARTING, state)

    def test_reset_arbitrary_changes_resets_changed_attributes(self):
        arbitrary_game = self._create_arbitrary_game()
        arbitrary_game.reset()
        assert_attributes_equal(self, self.ms, arbitrary_game, self.VALIDATE_ATTR)

    def test_update_down_command_before_start_does_not_start_game(self):
        self.ms.update(Command(CmdType.DOWN, 0, 0))
        self.assertEquals(((0, 1), State.STARTING),
                          (self.ms.cursor_pos, self.ms.game_state.state))

    def test_update_start_and_down_command_moves_cursor_down(self):
        self.ms._start()
        self.ms.update(Command(CmdType.DOWN, 0, 0))
        self.assertEquals((0, 1), self.ms.cursor_pos)

    def test_update_start_and_right_command_moves_cursor_right(self):
        self.ms._start()
        self.ms.update(Command(CmdType.RIGHT, 0, 0))
        self.assertEquals((1, 0), self.ms.cursor_pos)

    def test_update_start_and_flag_command_flags_cell(self):
        self.ms._start()
        self.ms.update(Command(CmdType.TOGGLE_FLAG, 0, 0))
        self.assertEquals(BoardState.FLAG, self.ms.board.get(0, 0))

    def test_update_start_and_reveal_command_reveals_cell(self):
        self.ms._start()
        self.ms.update(Command(CmdType.REVEAL, 0, 0))
        self.assertIn(self.ms.board.get(0, 0),
                [BoardState.MINE, BoardState.EMPTY] + list(range(1, 9)))


class TestBoardState(TestCase):
    @staticmethod
    def _create_boardstate(height=4, width=4, density=0.125):
        bs = BoardState(height, width, density)
        bs.reset()
        bs.create_mines()
        return bs

    def test_reset_arbitrary_board_returns_all_hidden(self):
        bs = self._create_boardstate()
        bs.set(1, 1, BoardState.FLAG)
        bs.reset()
        self.assertEquals(bs.get(1, 1), BoardState.HIDDEN)

    def test_width(self):
        bs = self._create_boardstate(width=7)
        self.assertEquals(7, bs.width)

    def test_height(self):
        bs = self._create_boardstate(height=5)
        self.assertEquals(5, bs.height)

    def test_num_mines_0_density_returns_1_mine(self):
        bs = self._create_boardstate(4, 4, density=0)
        self.assertEquals(1, bs.num_mines)

    def test_num_mines_half_density_returns_7_mines(self):
        bs = self._create_boardstate(4, 4, density=0.5)
        self.assertEquals(7, bs.num_mines)

    def test_num_mines_1_density_returns_15_mines(self):
        bs = self._create_boardstate(4, 4, density=1)
        self.assertEquals(15, bs.num_mines)

    def test_is_in_bounds_position_above_board_returns_false(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(1, -1)
        self.assertFalse(in_bounds)

    def test_is_in_bounds_position_below_board_returns_false(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(4, 1)
        self.assertFalse(in_bounds)

    def test_is_in_bounds_position_right_of_board_returns_false(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(4, 1)
        self.assertFalse(in_bounds)

    def test_is_in_bounds_position_left_of_board_returns_false(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(-1, 1)
        self.assertFalse(in_bounds)

    def test_is_in_bounds_position_on_top_edge_returns_true(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(1, 0)
        self.assertTrue(in_bounds)

    def test_is_in_bounds_position_on_bottom_edge_returns_true(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(1, 3)
        self.assertTrue(in_bounds)

    def test_is_in_bounds_position_on_right_edge_returns_true(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(3, 1)
        self.assertTrue(in_bounds)

    def test_is_in_bounds_position_on_left_edge_returns_true(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(0, 1)
        self.assertTrue(in_bounds)

    def test_is_in_bounds_position_on_board_returns_true(self):
        bs = self._create_boardstate(4, 4)
        in_bounds = bs.is_in_bounds(1, 1)
        self.assertTrue(in_bounds)

    def test_reveal_mines_half_filled_reveals_all_mines(self):
        bs = self._create_boardstate(4, 4, density=0.5)
        bs.reveal_mines()
        self.assertEqual(7, len([mine for _, _, mine in bs if mine == BoardState.MINE]))

    def test_reveal_from_adjacent_to_mine_reveals_one_cell(self):
        bs = self._create_boardstate(3, 3, 0)
        bs._mines = [(0, 0)]  # Single mine at origin
        bs.reveal_from(1, 1)
        self.assertEquals([[32, 32, 32],
                           [32, 1, 32],
                           [32, 32, 32]],
                          bs._rows)

    def test_reveal_from_away_from_mine_reveals_all_but_mine(self):
        bs = self._create_boardstate(3, 3, 0)
        bs._mines = [(0, 0)]  # Single mine at origin
        bs.reveal_from(2, 2)
        self.assertEquals([[32, 1, 0],
                           [1, 1, 0],
                           [0, 0, 0]],
                          bs._rows)

    def test_reveal_from_away_and_partially_blocked_reveals_half_board(self):
        bs = self._create_boardstate(3, 4, 0)
        bs._mines = [(1, 0), (1, 1)]  # Two mines down middle
        bs.reveal_from(3, 1)
        self.assertEquals([[32, 32, 2, 0],
                           [32, 32, 2, 0],
                           [32, 32, 1, 0]],
                          bs._rows)

    def test_set(self):
        bs = self._create_boardstate()
        bs.set(0, 0, 99)
        modified_cell = bs.get(0, 0)
        self.assertEquals(99, modified_cell)

    def test_get(self):
        bs = self._create_boardstate()
        cell = bs.get(0, 0)
        self.assertEquals(BoardState.HIDDEN, cell)

    def test_clamp_pos_outside_bottom_right_returns_bottom_right_corner(self):
        bs = self._create_boardstate()
        clamped_pos = bs.clamp_pos((9, 9))
        self.assertEquals((3, 3), clamped_pos)

    def test_clamp_pos_outside_top_left_returns_top_left_corner(self):
        bs = self._create_boardstate()
        clamped_pos = bs.clamp_pos((-9, -9))
        self.assertEquals((0, 0), clamped_pos)


class TestCommand(TestCase):
    def test_pos(self):
        command = Command(CmdType.REVEAL, 17, 19)
        self.assertEquals((17, 19), command.pos)


class TestMineSweeperModule(TestCase):
    def test_map_key_to_command(self):
        command = map_key_to_command(CmdKey.REVEAL_KEY, 0, 0)
        self.assertEquals(Command(CmdType.REVEAL, 0, 0), command)

    def test_map_cell_state_to_renderable(self):
        renderable = map_cell_state_to_renderable(BoardState.HIDDEN)
        self.assertEquals(Strings.HIDDEN_CELL, renderable)
