# pmine
Example code in Python 2.7+ / Python 3.6+ using only the standard library.

This is a terminal app that is installed as pmine. It requires support for
UTF-8 and curses. Entry point is in minesweeper_cli.py. Use the `-h` option
to print help.

```
Usage: pmine [difficulty [width [height]]] [-h] [-d] [-a]

  difficulty  Integer between 0 and 40 inclusive.
  width       Integer greater than 1.
  height      Integer greater than 1.

Options:
  -h  HelpDisplays this help message.
  -d  DebugDisplays complete call stacks on errors.
  -a  AutoEnables AI player to play 20 boards.

In game:
  Use the arrow keys or [hjkl] to move.
  Press [f] to flag a mine under cursor.
  Press [space] to reveal from under the cursor.
  Press [q] to quit the game.

There are no commands when AI player is enabled.

Example:
> pmine 3 32 16 -a

  This will have the AI player attempt 32x16 boards moderately packed
  with mines.
```

![Title](https://raw.githubusercontent.com/kindjie/minesweeper/main/readme/title.png)
![Hidden Board](https://raw.githubusercontent.com/kindjie/minesweeper/main/readme/hidden_board.png)
![Active Board](https://raw.githubusercontent.com/kindjie/minesweeper/main/readme/active_board.png)
![Defeat](https://raw.githubusercontent.com/kindjie/minesweeper/main/readme/defeat.png)
