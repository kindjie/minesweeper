#!/usr/bin/env python
# coding=utf-8
import itertools
import sys
import time
from collections import deque
from collections import namedtuple
from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from random import sample

from game import State, BoardGameState
from renderer import start_loop


class MineSweeper(object):
    DIFFICULTY_STEP = 0.025

    def __init__(self, width, height, difficulty):
        max_difficulty = int(1.0 / self.DIFFICULTY_STEP)
        if not 0 <= difficulty <= max_difficulty:
            raise ValueError('Invalid difficulty: 0 <= [%s] <= %s' % (difficulty, max_difficulty))

        self._board = BoardState(height, width, self.DIFFICULTY_STEP * difficulty)
        self.reset()

    @property
    def cursor_pos(self):
        return self._cursor_pos

    @property
    def board(self):
        return self._board

    @property
    def game_over(self):
        return self._state & State.GAME_OVER

    @property
    def game_state(self):
        return BoardGameState(self.board, self.cursor_pos, self._state)

    def reset(self):
        self.title = Strings.TITLE
        self.footer = Strings.FOOTER
        self.message = ''
        self._state = State.STARTING
        self._cursor_pos = (0, 0)
        self._num_flags = 0
        self._num_mines_flagged = 0
        self._start_time = 0
        self._board.reset()

    def update(self, command):
        if self._state & State.STARTING:
            self._start()
            return

        if command is None or command.type == CmdType.NONE or self.game_over:
            return

        self._handle_movement(command)
        self._handle_reveal(command)
        self._handle_toggle_flag(command)

    def _start(self):
        self._state = State.ACTIVE
        self._start_time = time.time()

    def _end(self, is_victory):
        if is_victory:
            self._state = State.VICTORY
            self.message = Strings.VICTORY
        else:
            self._board.reveal_mines()
            self._state = State.DEFEAT
            self.message = Strings.DEFEAT

        total_time = time.time() - self._start_time
        self.message += Strings.TIMER % total_time

    def _handle_movement(self, command):
        new_cursor_pos = list(command.pos)
        if command.type & CmdType.DOWN:
            new_cursor_pos[1] += 1
        if command.type & CmdType.LEFT:
            new_cursor_pos[0] -= 1
        if command.type & CmdType.RIGHT:
            new_cursor_pos[0] += 1
        if command.type & CmdType.UP:
            new_cursor_pos[1] -= 1

        self._cursor_pos = tuple(self._board.clamp_pos(new_cursor_pos))

    def _handle_reveal(self, command):
        if not command.type & CmdType.REVEAL:
            return

        if self._board.get(*command.pos) != self._board.HIDDEN:
            return

        if self._cursor_pos in self._board._mines:
            self._end(False)
        else:
            self._board.reveal_from(*self.cursor_pos)

    def _handle_toggle_flag(self, command):
        if not command.type & CmdType.TOGGLE_FLAG:
            return

        if self._board.get(*self._cursor_pos) == self._board.HIDDEN:
            self._board.set(*self.cursor_pos, value=self._board.FLAG)
            self._num_flags += 1

            if command.pos in self._board._mines:
                self._num_mines_flagged += 1

            if self._all_mines_found():
                self._end(True)
        else:
            self._board[self._cursor_pos[1]][self._cursor_pos[0]] = self._board.HIDDEN
            self._num_flags -= 1

            if command.pos in self._board._mines:
                self._num_mines_flagged -= 1

        self.title = Strings.TITLE + Strings.FLAG_COUNT % (self._num_flags, self._board.num_mines)

    def _all_mines_found(self):
        all_flagged = self._num_mines_flagged == self._board._num_mines
        no_empty_flagged = self._num_mines_flagged <= self.board.num_mines
        return all_flagged and no_empty_flagged


class BoardState(object):
    EMPTY = 0
    # Reserved 1-8 for mine counts.
    HIDDEN = 1 << 5
    MINE = 1 << 6
    FLAG = 1 << 7

    Cell = namedtuple('Cell', ['x', 'y', 'state'])

    def __init__(self, height, width, density=0.125):
        if not 0.0 <= density <= 1.0:
            raise ValueError('Invalid density: 0.0 <= [%s] <= 1.0' % density)
        if width <= 1:
            raise ValueError('Invalid _width: [%s] > 1' % width)
        if height <= 1:
            raise ValueError('Invalid _height: [%s] > 1' % height)

        self._width = width
        self._height = height
        max_possible_mines = (self._width * self._height) - 1
        self._num_mines = max(1, int(max_possible_mines * density))  # At least 1 mine.
        self.reset()

    def reset(self):
        self._mines = set(self._create_mines())
        self._rows = [[self.HIDDEN for _ in xrange(self._width)] for _ in xrange(self._height)]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def num_mines(self):
        return self._num_mines

    def is_in_bounds(self, x, y):
        return 0 <= x < self._width and 0 <= y < self._height

    def reveal_mines(self):
        for mine in self._mines:
            self.set(*mine, value=self.MINE)

    def reveal_from(self, x, y):
        visited = set()
        to_visit = deque()
        to_visit.append((x, y))

        def fill(x, y):
            if not self.is_in_bounds(x, y) or (x, y) in visited:
                return

            visited.add((x, y))

            num_adjacent_mines = self._count_adjacent_mines(x, y)
            if num_adjacent_mines > 0:
                self._rows[y][x] = num_adjacent_mines
            else:
                self._rows[y][x] = self.EMPTY
                for pos in self._adjacent_pos(x, y):
                    to_visit.append(pos)

        while len(to_visit) > 0:
            fill(*to_visit.pop())

    def set(self, x, y, value):
        if self.is_in_bounds(x, y):
            self._rows[y][x] = value

    def get(self, x, y):
        return self._rows[y][x] if self.is_in_bounds(x, y) else None

    def clamp_pos(self, pos):
        return (min(self._width - 1, max(pos[0], 0)),
                min(self._height - 1, max(pos[1], 0)))

    def _adjacent_pos(self, x, y):
        return set(itertools.product([x - 1, x, x + 1], [y - 1, y, y + 1]))

    def _create_mines(self):
        return sample(list(itertools.product(xrange(self._width), xrange(self._height))),
                      self._num_mines)

    def _count_adjacent_mines(self, x, y):
        return len(self._adjacent_pos(x, y).intersection(self._mines))

    def __iter__(self):
        return (self.Cell(x, y, self._rows[y][x])
                for y in xrange(len(self._rows))
                for x in xrange(len(self._rows[0])))

    def __getitem__(self, row):
        return self._rows[row]

    def __len__(self):
        return len(self._rows)

    def __repr__(self):
        return '[%s]' % (',\n '.join(str(row) for row in self._rows))

    def __eq__(self, other):
        return all(other.get(x, y) == state for x, y, state in self)

    def __neq__(self, other):
        return not self == other


class Command(namedtuple('Command', ['type', 'x', 'y'])):
    @property
    def pos(self):
        return self.x, self.y


class CmdType(object):
    NONE = 0

    TOGGLE_FLAG = 1 << 1

    REVEAL = 1 << 3

    LEFT = 1 << 5
    RIGHT = 1 << 6
    UP = 1 << 7
    DOWN = 1 << 8
    MOVE = LEFT | RIGHT | UP | DOWN


class CmdKey(object):
    MOVEMENT_KEYS = {
        KEY_DOWN: CmdType.DOWN,
        KEY_LEFT: CmdType.LEFT,
        KEY_RIGHT: CmdType.RIGHT,
        KEY_UP: CmdType.UP
    }
    REVEAL_KEY = ord(' ')
    TOGGLE_FLAG_KEY = ord('f')
    QUIT_KEY = ord('q')


def map_key_to_command(key_code, x, y):
    if key_code == CmdKey.QUIT_KEY:
        raise StopIteration()

    if key_code in CmdKey.MOVEMENT_KEYS:
        return Command(CmdKey.MOVEMENT_KEYS[key_code], x, y)

    elif key_code == CmdKey.REVEAL_KEY:
        return Command(CmdType.REVEAL, x, y)

    elif key_code == CmdKey.TOGGLE_FLAG_KEY:
        return Command(CmdType.TOGGLE_FLAG, x, y)

    return Command(CmdType.NONE, x, y)


def map_cell_state_to_renderable(cell):
    if cell == BoardState.HIDDEN:
        return Strings.HIDDEN_CELL

    if cell == BoardState.MINE:
        return Strings.MINE_CELL

    if cell == BoardState.FLAG:
        return Strings.FLAG_CELL

    if cell == BoardState.EMPTY:
        return Strings.EMPTY_CELL

    try:
        if 0 < int(cell) <= 8:
            return str(cell)
    except ValueError:
        # Invalid cell state.
        pass

    return Strings.INVALID_CELL


class Strings(object):
    TITLE = u'MineSweeper'
    FOOTER = u'[←][↑][→][↓] [Space] [f] [q]'
    FLAG_COUNT = u' - [%s / %s]'
    TIMER = u' - [%is]'
    VICTORY = u'VICTORY!'
    DEFEAT = u'DEFEAT'

    HIDDEN_CELL = u'·'
    MINE_CELL = u'[bold]¤'
    FLAG_CELL = u'[bold]†'
    EMPTY_CELL = u' '
    INVALID_CELL = u'?'


# Commandline
def main(difficulty=3, width=32, height=16):
    minesweeper = MineSweeper(width, height, difficulty)
    start_loop(minesweeper, map_cell_state_to_renderable, map_key_to_command)


def usage(error):
    print 'Usage:\n\t%s [difficulty [width [height]]] [-h] [-d]\n%s' % (sys.argv[0], error)


if __name__ == '__main__':
    debug = '-d' in sys.argv
    if debug:
        sys.argv.remove('-d')
    try:
        if len(sys.argv) == 1:
            main()
        elif '-h' not in sys.argv:
            main(*map(int, sys.argv[1:]))
    except Exception as e:
        usage(e)
        if debug:
            raise
