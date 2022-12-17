# JoshGone

A Discord bot with some random commands.

## Setup

Clone the repo using [Git](https://git-scm.com/downloads) and enter it using the commands below:

```sh
git clone https://github.com/GeeTransit/joshgone
cd joshgone
```

Install [Python](https://www.python.org/downloads/) (minimum is 3.9).

Install [Hatch](https://ofek.dev/hatch/latest/install/) globally (I recommend using [pipx](https://pypa.github.io/pipx/installation/)) (also note that Hatch is in prerelease; pass `--pre` where necessary).

## Config

JoshGone takes all configuration using environment variables. Here's a table with the environment variables needed.

| Name           | Purpose                                                      |
| -------------- | ------------------------------------------------------------ |
| JOSHGONE_TOKEN | Discord bot user's token. Should be around 59 characters long and look random. |
| JOSHGONE_DB    | SQLite database location. Set it to `joshgone.db`.           |
| JOSHGONE_REPL  | Optional. Can be `0` (default) or `1`. If it is `1`, there will be a REPL after the bot starts. |

You can get your Discord bot user's token by going to [your dashboard](https://discord.com/developers/applications), clicking on your application, clicking *Bot* in the left sidebar, and pressing the *Copy* button under *Token* in the *Build-A-Bot* section.

If you don't have an application, click *New Application* on the top right and choose a name (you can change it later).

If you don't have a bot user, press *Add Bot* in the *Build-a-Bot* section and click *Yes, do it!*

To set an environment variable, run:

```sh
# On Windows
set NAME=value
# On Linux
export NAME=value
```

## More Setup

Create or update the database to the newest format by running:

```sh
hatch run yoyo apply
```

For playing music to work, you need to have [FFmpeg](http://ffmpeg.org/) on your PATH environment variable. Verify by running:

```sh
ffmpeg -version
```

## Usage

Run:

```sh
hatch run python joshgone.py
```

## Online Sequencer

*Note: This is very experimental.*

For playing music from Online Sequencer to work, use `hatch -e os ...` instead of `hatch ...` to use the OS environment (which has extra dependencies). For more info on how it gets the sequence notes, check out `online_sequencer_get_note_infos.py`.

Next, run the following command. This will download the instrument settings and the audio file for each instrument into a directory named oscollection.

```sh
hatch -e os run python online_sequencer_download.py oscollection
```

If you want to use a different directory name, replace oscollection with the different name in the command, and set the JOSHGONE_OS_DIRECTORY environment variable to the different name.

### PyPy

[PyPy](https://www.pypy.org/) can significantly reduce lag in processing the sequence. If you have it installed, you can set the JOSHGONE_OS_PY_EXE environment variable to a different Python executable to run `online_sequencer_make_chunks.py` with.

Note that the script requires some libraries, meaning you'll need a virtual environment for PyPy. You can write a script for your platform, but my suggestion is to use [pew](https://github.com/berdario/pew), a cross platform wrapper around virtual environments. Note that I've created a fork of the project with a new `pew inraw` command that works better with `subprocess.run` and the like. You can install it using one of the following commands (more info on pipx [here](https://pypa.github.io/pipx/)):

```sh
# On Windows
pip install git+https://github.com/GeeTransit/pew.git
# On Linux
pip3 install git+https://github.com/GeeTransit/pew.git
# With pipx
pipx install git+https://github.com/GeeTransit/pew.git
```

You can then initialize a PyPy virtual environment by running the following:

```sh
# Create a new virtual environment using PyPy (-p pypy3) and don't enter it (-d)
pew new joshgone-pypy -p pypy3 -d
# Install packages in the virtual environment
pew inraw joshgone-pypy pip install -r requirements-soundit.txt
```

You can then set JOSHGONE_OS_PY_EXE to `pew inraw joshgone-pypy pypy3` for it to run PyPy inside the virtual environment, where it can access the libraries it needs.

## Todo
- Maybe refork entire bot to deal for a clean start (databases might be useful) - songs + geelang
