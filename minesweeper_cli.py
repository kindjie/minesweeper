#!/usr/bin/env python
import sys
from _curses import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP

from minesweeper import MineSweeper, map_cell_state_to_renderable, CmdType, Command
from minesweeper_ai import MineSweeperAI
from renderer import start_loop


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




def main(difficulty=3, width=32, height=16, auto=False):
    minesweeper = MineSweeper(width, height, difficulty)
    ai = MineSweeperAI(minesweeper) if auto else None
    start_loop(minesweeper, map_cell_state_to_renderable, map_key_to_command, ai)
    print 'Victories: %s\tDefeats: %s\t%% Wins: %.2f' % (minesweeper.num_victories,
                                                         minesweeper.num_defeats,
                                                         minesweeper.fraction_wins * 100.0)


def usage():
    print 'Usage:\n\t%s [difficulty [width [height]]] [-h] [-d]' % sys.argv[0]


if __name__ == '__main__':
    auto = '-a' in sys.argv
    debug = '-d' in sys.argv
    help = '-h' in sys.argv

    if debug:
        sys.argv.remove('-d')

    if auto:
        sys.argv.remove('-a')

    if help:
        usage()
    else:
        try:
            main(*map(int, sys.argv[1:]), auto=auto)
        except Exception as e:
            usage()
            if debug:
                raise
            else:
                print e
