import curses
import locale
import re

from minesweeper.game import State


class Window(object):
    def __init__(self, lines=None, cols=None):
        self.window = None
        self._dimensions = (lines, cols)

    def __enter__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.window = curses.initscr()
        self.window.keypad(1)
        if self._dimensions is not None:
            self.window.resize(*self._dimensions)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        return self.window

    def __exit__(self, exc_type, exc_val, exc_tb):
        curses.curs_set(2)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


class GameBoardRenderer(object):
    STYLES = {
        'bold': curses.A_BOLD,
        'blink': curses.A_BLINK,
        'reverse': curses.A_REVERSE,
        'dim': curses.A_DIM,
    }

    BORDER_WIDTH = 1

    def __init__(self, window):
        self._game_window = window
        self._lines, self._cols = window.getmaxyx()
        self._title_window = window.derwin(1, self._cols - 2 * self.BORDER_WIDTH,
                                           0, self.BORDER_WIDTH)
        self._footer_window = window.derwin(1, self._cols - 2 * self.BORDER_WIDTH,
                                            self._lines - 1, self.BORDER_WIDTH)
        self.title = ''
        self.footer = ''
        self.message = ''

    def render(self, map_cell_to_renderable, board_game_state):
        board_state, cursor_pos, game_state = board_game_state

        self._game_window.border()
        if not self._is_valid_board_state(board_state):
            raise ValueError('Invalid _rows state: %s' % board_state)

        for x, y, state in board_state:
            self._put_on_board(x, y, map_cell_to_renderable(state))

        self._game_window.move(cursor_pos[1] + self.BORDER_WIDTH,
                               cursor_pos[0] + self.BORDER_WIDTH)
        self._render_labels()
        self._render_game_over(game_state)
        self._game_window.refresh()

    def _render_game_over(self, game_state):
        if game_state & State.GAME_OVER:
            curses.curs_set(0)
            if game_state & State.DEFEAT:
                curses.flash()
        else:
            curses.curs_set(2)

    def _render_labels(self):
        self._put_title(self.title)
        self._put_footer(self.footer)
        self._put_center(self.message)

    def _put(self, window, text, x=0, y=0, style=curses.A_BOLD):
        if not text:
            return

        try:
            window.addstr(y, x, text.encode('utf8'), style)
        except:
            # Ignore error if text is too long.
            pass

    def _put_on_board(self, x, y, text):
        if not self.is_in_board_bounds(x, y):
            raise ValueError("%d, %d is out of window bounds" % (x, y))

        style, char = self._parse_style(text)
        if len(char) > 1:
            raise ValueError('Invalid char: %s' % char)

        self._put(self._game_window, char, x + self.BORDER_WIDTH, y + self.BORDER_WIDTH, style)

    def _put_title(self, text):
        self._put(self._title_window, text)

    def _put_footer(self, text):
        self._put(self._footer_window, text)

    def _put_center(self, text):
        max_lines, max_cols = self._game_window.getmaxyx()
        padded_text = self._pad_text(text)
        x = max_cols // 2 - len(padded_text) // 2
        y = max_lines // 2
        self._put(self._game_window, padded_text, x, y, curses.A_REVERSE | curses.A_BOLD)

    def is_in_board_bounds(self, x, y):
        return 0 <= y < self._lines - 2 * self.BORDER_WIDTH and \
               0 <= x < self._cols - 2 * self.BORDER_WIDTH

    def _parse_style(self, styled_text):
        style_groups = re.match(r'^\[(\w+)\](.*)$', styled_text)
        if style_groups is None:
            return 0, styled_text
        style, text = self.STYLES[style_groups.group(1)], style_groups.group(2)
        return style, text

    def _pad_text(self, text, left_pad=1, right_pad=1, fill_char=' '):
        if not text:
            return ''
        return '%s%s%s' % (fill_char * left_pad, text, fill_char * right_pad)

    def _is_valid_board_state(self, board_state):
        return board_state is not None and \
               len(board_state) > 0 and \
               len(board_state[0]) > 0


class GameBoardInputHandler(object):
    def __init__(self, window, transform_key_to_command):
        '''
        Iterator that reads input from curses window and returns a series of commands.
        :param window: Valid curses window.
        :param transform_key_to_command: Callable that returns game commands.
        '''
        self.prev_input_code = None
        self.prev_cursor_coord = 0, 0
        self.window = window
        self.transform = transform_key_to_command

    def __iter__(self):
        return self

    def next(self):
        self.prev_input_code = self.window.getch()
        self.prev_cursor_coord = self.window.getyx()
        return self.transform(self.prev_input_code,
                              self.prev_cursor_coord[1] - GameBoardRenderer.BORDER_WIDTH,
                              self.prev_cursor_coord[0] - GameBoardRenderer.BORDER_WIDTH)
    __next__ = next


def start_loop(game, map_cell_to_renderable, map_key_to_command, ai):
    with Window(game.board.height + 2 * GameBoardRenderer.BORDER_WIDTH,
                game.board.width + 2 * GameBoardRenderer.BORDER_WIDTH) as game_window:
        game_renderer = GameBoardRenderer(game_window)
        game_input_handler = GameBoardInputHandler(game_window, map_key_to_command) if ai is None \
                             else ai

        game_renderer._put_center(game.title)

        for command in game_input_handler:
            if game.game_over:
                game.reset()

            game.update(command)

            game_renderer.title = game.title
            game_renderer.footer = game.footer
            game_renderer.message = game.message

            game_renderer.render(map_cell_to_renderable, game.game_state)
