from collections import namedtuple


class State(object):
    STARTING = 1<<0

    MENU = 1<<2

    ACTIVE = 1<<4

    VICTORY = 1<<8
    DEFEAT = 1<<9
    GAME_OVER = VICTORY | DEFEAT


BoardGameState = namedtuple('BoardGameState', ['board', 'cursor_pos', 'state'])
