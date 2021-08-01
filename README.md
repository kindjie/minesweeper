# minesweeper
Example code in Python 2.7+ / Python 3.6+ using only the standard library.
This a terminal app that requires support for UTF-8 and curses. Entry point
is in minesweeper_cli.py. Use the `-h` option to print help.

```
Usage: minesweeper_cli [difficulty [width [height]]] [-h] [-d] [-a]

  difficulty  Integer between 0 and 40 inclusive.
  width       Integer greater than 1.
  height      Integer greater than 1.

Options:
  -h  HelpDisplays this help message.
  -d  DebugDisplays complete call stacks on errors.
  -a  AutoEnables AI player.

In game:
  Use the arrow keys or [hjkl] to move.
  Press [f] to flag a mine under cursor.
  Press [space] to reveal from under the cursor.
  Press [q] to quit the game.

There are no commands when AI player is enabled.
```

![Title](./readme/title.png)
![Hidden Board](./readme/hidden_board.png)
![Active Board](./readme/active_board.png)
![Defeat](./readme/defeat.png)
