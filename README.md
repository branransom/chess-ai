# Chess AI

Teaching a computer how to play chess.

## Usage

The easiest way to play against this chess engine is by challenging it to a game on lichess: https://lichess.org/@/brandobot

It has not been optimized for performance yet, so classical games are preferred.

The engine is now running on a `t2.micro` AWS EC2 instance.

## How to Run on lichess

### Creating binary file

If running in a virtual env (e.g. `pyenv`), you must run `pyinstaller` in the context of that virtual env:

```
pip install pyinstaller
pyinstaller src/main.py
```

This will generate the binary files in `dist/main`. These files can then be ported over to the `lichess-bot` directory, which provides a bridge to `lichess`. The bridge uses UCI commands to communicate with the chess engine, so the chess engine has a communication layer that will interpret the commands accordingly. These same commands can be provided directly to the chess engine outside of the `lichess` context for debugging purposes.

### Running on lichess

This project provides a bridge between a chess bot and lichess: https://github.com/ShailChoksi/lichess-bot

Clone the repository as a sibling to this repo. Installation instructions can be found in its `README`.

After running `pyinstaller` to create a binary file, run:

```
cp -r ./dist/main/** ../lichess-bot/engines
```

Then, after following installation instructions for `lichess-bot`, run `python lichess-bot.py` in the `lichess-bot` directory.

## Debugging

Debugging the decision tree is difficult, especially at greater depths. I need to iterate on the debugging capabilities to better understand how the engine is making decisions in specific positions. Currently, I have created a module that mimics the `move_generator` logic, but generates a tree map of considered moves and their calculated values. The library used to manage the nodes of the tree is [treelib](https://treelib.readthedocs.io/en/latest/)

There is logic in the debug module to generate a file that's interpretable by [Graphviz](https://graphviz.org/). A visual graph of the tree can be generated by running the following command on the generated file (where `decision_tree` is the arbitrarily-named file generated by my debug flow): `dot -T png decision_tree -o output.png`

## TODO

- [x] Implement minimax
- [x] Add alpha beta pruning
- [x] Add quiescence search
- [x] Cache position value lookups
- [x] Connect to `lichess` using UCI
- [x] Run on a cloud instance to improve availability
- [x] Create debug plugin for `move_generator` module to generate decision tree for specific moves
- [x] Improve sorting of moves (MVV-LVA -- https://www.chessprogramming.org/MVV-LVA)
- [x] Implement transposition table
- [ ] Implement principle variation
- [ ] Implement iterative deepening search
- [ ] Add tests (functional/performance)
- [ ] Set up automated pipeline to run tests and deploy
- [ ] Implement parallel processing to use multiple cores
- [ ] Manage AWS resources using CDK
- [ ] Reinforcement learning?
