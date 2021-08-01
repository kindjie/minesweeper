#!/usr/bin/env python
import os
import sys
from _curses import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP

from minesweeper.minesweeper import MineSweeper, map_cell_state_to_renderable, CmdType, Command
from minesweeper.minesweeper_ai import MineSweeperAI
from minesweeper.renderer import start_loop


class CmdKey(object):
    REVEAL_KEY = ord(' ')
    TOGGLE_FLAG_KEY = ord('f')
    QUIT_KEY = ord('q')
    J_KEY = ord('j')
    K_KEY = ord('k')
    H_KEY = ord('h')
    L_KEY = ord('l')

    MOVEMENT_KEYS = {
        KEY_DOWN: CmdType.DOWN,
        KEY_LEFT: CmdType.LEFT,
        KEY_RIGHT: CmdType.RIGHT,
        KEY_UP: CmdType.UP,

        J_KEY: CmdType.DOWN,
        K_KEY: CmdType.UP,
        H_KEY: CmdType.LEFT,
        L_KEY: CmdType.RIGHT
    }


def map_key_to_command(key_code, x, y):
    if key_code == CmdKey.QUIT_KEY:
        raise StopIteration()

    if key_code in CmdKey.MOVEMENT_KEYS:
        return Command(CmdKey.MOVEMENT_KEYS[key_code], x, y)

    if key_code == CmdKey.REVEAL_KEY:
        return Command(CmdType.REVEAL, x, y)

    if key_code == CmdKey.TOGGLE_FLAG_KEY:
        return Command(CmdType.TOGGLE_FLAG, x, y)

    return Command(CmdType.NONE, x, y)




def main(difficulty=3, width=32, height=16, auto=False):
    minesweeper = MineSweeper(width, height, difficulty)
    ai = MineSweeperAI(minesweeper) if auto else None
    start_loop(minesweeper, map_cell_state_to_renderable, map_key_to_command, ai)
    print('Victories: %s\tDefeats: %s\t%% Wins: %.2f' % (minesweeper.num_victories,
                                                         minesweeper.num_defeats,
                                                         minesweeper.fraction_wins * 100.0))


def usage():
    caller = os.path.basename(sys.argv[0])
    print(  'Usage:\n'
            '     %s [difficulty [width [height]]] [-h] [-d] [-a]\n'
            '\n'
            '     difficulty   Integer between 0 and 40 inclusive.\n'
            '     width        Integer greater than 1.\n'
            '     height       Integer greater than 1.\n'
            '\n'
            'Options:\n'
            '    -h Help       Displays this help message.\n'
            '    -d Debug      Displays complete call stacks on errors.\n'
            '    -a Auto       Enables AI player to play 20 boards.\n'
            '\n'
            'In game:\n'
            '     Use the arrow keys or [hjkl] to move.\n'
            '     Press [f] to flag a mine under cursor.\n'
            '     Press [space] to reveal from under the cursor.\n'
            '     Press [q] to quit the game.\n'
            '\n'
            'There are no commands when AI player is enabled.\n'
            '\n'
            'Example:\n'
            '     > pmine 3 32 16 -a\n'
            '\n'
            '     This will have the AI player attempt 32x16 boards moderately packed\n'
            '     with mines.' % caller)


def start():
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
            print(e)

if __name__ == '__main__':
    start()
