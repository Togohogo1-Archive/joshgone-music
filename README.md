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

## TODO
- Note about guild_join server table ;running command combo causing chants to work
- Note about adding extensions
- Notes about installation
- Hatch file generations
- Clean up the database generation (some stuff aren't necessary anymore)
- Options is single quote, before options is double quote
- `self.var` <- double check for consiststency
- Make volume a permanent setting?
- Inconsistency in error quotes (`ExtensionNotFound` vs `CommandNotFound` single & double quotes)

## Features in v2.0.0
- [x] Seeking forward and backward
- [x] Sleep timer
    - Sleep in hh:mm:ss or just raw seconds
- [x] Goto
    - Go to hh:mm:ss
    - ~~Use fast ff and rw if time difference is less than x minutes (set to 10?)~~
    - Seems like VLC android doesn't allow jumping to ms
- [x] Autoshuffle
    - Shuffle
- [x] Loop current song
    - Continuous play the current song
- [x] More detailed song info
    - length
    - file size?
    - 0:00/5:00
    - codec
    - sample rate
    - metadata
- [x] Playback speed
    - A value between 0.25 and 4
    - ^ if that's too laggy then to 0.5 to 2
    - Will be applied on next song
- [x] Filters
    - Present, some examples include:
    - Nightcore
    - Daycore
    - Bass boost
    - Vaporwave (reverb)
    - Radio
    - Will require complete redesign of `_DEFAULT_FFMPEG_OPTS`
- [x] Append command
    - Appends at the front of the list instead of teh back
- [x] Forceskip (not practical, more of a meme command)
- [x] A more watered down version of play previous song
    - Store a queue of previously played song (history command)
    - `;prev` removes last played song in history and adds to the end of queue
    - `;pprev` removes last played song in history and adds to the start of queue
    - Size of history queue capped at some number (I'm thinking 15)
    - Or only keep previously played and full playback history
- [x] Playback history (subset of previous)
- [x] Migrate to discord.py 2.0 to use apiv10
- Extra decorations
    - Typing indicator in channel
    - Disable is live feature
    - Command sorting (more vs filters)

## Features in v2.1.0
- [ ] Better local file support
    - Cap on file directory size
- [ ] Better playlist support
- [ ] Figure out database (playlist) importing exporting
- [ ] Soundcloud playlists
- [ ] Better reloading and unloading

## Eventually in a future version
- [ ] Add slash commands functionality

## VLC features that may not be implemented
- Stop after some track
- Song bookmarking (bookmark song at 1:25)
- The ability to sort tracks (might make an exception for playlists tho)
- ABrepeat
- Full on customized equalizer

## Random cases that might cause the bot to break or unexpected behaviour
- when ;ff 15 for a long song, then do ;s or other commands
- when ;jump x:xx for a long song, then do other commands
- when ;batch_add a bunch of songs, do a ;ff when a current one is playing
- when ;batch_add a bunch of songs, do a ;jump x:xx when a current one is playing
- when ;jump x:xx causes a large delay, change the ffmpeg settings

## Short term todo
- Reorgainze commands based on simple/advanced/filter usage
- Continue making the bot unreloadable by hardcoding unload/load functions in `admin.py`
- Write a basic first-level help description for each command
- Move some instance variables into `self.data` so running the bot in 2 servers at a time doesn't cause issues

## Longer term goals
- More organized error messages
- Know where to use before/after_invoke decorators

```
Chant:
  chant            Repeat a chant multiple times
  chant1           Repeats a chant once
  chants           Configure chants
Database:
  reinit
  running
Filters:
  bassboost
  daycore
  deepfry
  defaults
  nightcore
  normal
  speed
More:
  _add_playlist    Adds all songs in a playlist to the queue
  cancel
  fast_forward
  forceskip
  jump
  rewind
  local            Plays a file from the local filesystem
  reschedule       Reschedules the current guild onto the advancer task
  sleepin
Music:
  autoshuffle
  batch_add        Plays from multiple urls split by lines
  clear            Clears all songs on queue
  current          Shows the current song
  info
  join             Joins a voice channel
  leave            Disconnects the bot from voice and clears the queue
  loop             ;loop q(queue) c(current) n(none) <>
  move             Moves a song on queue
  pause            Pauses playing
  playback_history
  queue            Shows the songs on queue
  remove           Removes a song on queue
  resume           Resumes playing
  shuffle          Shuffles the queue
  skip             Skips current song
  stream           Plays from a url (almost anything youtube_dl supports)
  stream_prepend   Plays from a url (almost anything youtube_dl supports)
  volume           Gets or changes the player's volume
​No Category:
  help             Shows this message

Type ;help command for more info on a command.
You can also type ;help category for more info on a category.
```

## Issues to be addressed
- Having the bot in multiple servers (instance variables not guild specific
)
- Spamming `;ff` or `;s` causes the bot to freeze if advancer isn't forced
- Python 3.10 `collections.abc` issue
