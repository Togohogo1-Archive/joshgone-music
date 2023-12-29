---
title: Setup
---

## Getting Started

Clone the repo using <a href="https://git-scm.com/downloads" target="_blank">Git</a> and enter it using the commands below:

```sh
git clone https://github.com/Togohogo1/jgmusic
cd jgmusic
```

Install <a href="https://www.python.org/downloads/" target="_blank">Python</a> (minimum is 3.10).

Install <a href="https://ofek.dev/hatch/latest/install/" target="_blank">Hatch</a> globally, recommended via <a href="https://pypa.github.io/pipx/installation/" target="_blank">pipx</a>.

??? note

    Hatch is in prerelease; pass `--pre` where necessary.

## Config

JoshGone Music takes all configuration using environment variables. Here's a table with the environment variables needed.

| Name           | Purpose                                                      |
| -------------- | ------------------------------------------------------------ |
| `JGM_TOKEN` | Discord bot user's token. Should be around 59 characters long and look random. |
| `JGM_DB`    | SQLite database location. Set it to `jgm.db`.           |
| `JGM_REPL`  | Optional. Can be `0` (default) or `1`. If it is `1`, there will be a REPL after the bot starts. |

For instructions on getting a Discord bot token and bot setup in general, visit <a href="https://discordpy.readthedocs.io/en/stable/discord.html" target="_blank">the official documentation</a>.

To set an environment variable, run:

=== "Windows"

    ```sh
    set NAME=value
    ```

=== "Mac/Linux"

    ```sh
    export NAME=value
    ```

## More Setup

Create or update the database to the newest format by running:

```sh
hatch run yoyo apply
```

For playing music, <a href="http://ffmpeg.org/" target="_blank">FFmpeg</a> must exist on the `PATH` environment variable. Verify by running:

```sh
ffmpeg -version
```

??? warning

    Some of the bot's features (pitch and tempo shifting) require FFmpeg to be compiled with <a href="https://ffmpeg.org/ffmpeg-filters.html#rubberband" target="_blank">librubberband</a>. You can check if this is the case by seeing if the `--enable-librubberband` compilation flag is listed under `configuration:` after running the above command. If this is not the case, then the commands related to pitch and tempo shifting will cause issues.

    Installing a FFmpeg binary from a common installation source (see *Get packages & executable files* under the FFmpeg downloads <a href="https://ffmpeg.org/download.html" target="_blank">page</a>) will usually include everything required for normal operation of the bot.

## Usage

To run the bot, simply do:

```sh
hatch run jgm
```

## Docs

To build the documentation from source, run:

```sh
hatch env run -e docs serve
```
