# Chess AI

Teaching a computer how to play chess (badly).

## Creating binary file

If running in a virtual env (e.g. `pyenv`), you must run `pyinstaller` in the context of that virtual env:

```
pip3 install pyinstaller
python3 -m PyInstaller main.py
```

## Running on lichess

This project provides a bridge between a chess bot and lichess: https://github.com/ShailChoksi/lichess-bot

Clone the repository as a sibling to this repo. Installation instructions can be found in its `README`.

After running `pyinstaller` to create a binary file, run:

```
cp -r ./dist/main/** ../lichess-bot/engines
cp -r ./model ../lichess-bot
```

Then, after following installation instructions for `lichess-bot`, run `python -m lichess-bot` in the `lichess-bot` directory. It's important to run it this way, because unexpected errors could occur if not run in the virtual env.
