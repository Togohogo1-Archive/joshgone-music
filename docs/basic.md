---
title: Basic Features
---

## Overview

The table below summarizes all the commands for basic bot usage. Click on any of them for more details, including special use cases, caveats, etc.

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;batch-add`](#batch_add) `<urls>` | | 2s | Plays from multiple URLs split by lines |
| [`;clear`](#clear)    |   | 1s | Clears all songs in queue |
| [`;current`](#current) | `;c` | 0.5s | Shows the current song |
| [`;join`](#join) `<channel>`  | | 1s | Joins a voice channel |
| [`;leave`](#leave)   |  | 1s | Disconnects the bot from voice and clears the queue |
| [`;loop`](#loop) `[loop]`  | | 1s | Gets or sets queue looping |
| [`;move`](#move) `<origin> <target>`  | `;mv` | 1s | Moves a song on queue |
| [`;pause`](#pause)   | `;stop` | 0.5s | Pauses playing |
| [`;queue`](#queue)   | `;q` | 1s | Shows the songs on queue |
| [`;remove`](#remove) `<position>` | `;rm` | 1s | Removes a song on queue |
| [`;resume`](#resume)   | `;start` | 0.5s | Resumes playing |
| [`;shuffle`](#shuffle)   | `;shuffle` | 1s | Shuffles the queue |
| [`;skip`](#skip)   | `;s` | 1s | Skips current song |
| [`;stream`](#stream) `<url>`  | `;yt`, `;play`, `;p` | 1s | Plays from a url (almost anything yt-dlp supports) |
| [`;volume`](#volume) `[volume]`  | | 1s | Gets or changes the player's volume |

[^1]: `[optinal argument] <required arguiment>`

## Commands

Recategorize them later

### [`batch_add`](#batch_add)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Plays from multiple URLs split by lines.

Splits the URLs by appropriate line termination character and individually [`stream`](#stream)s each query. Does not support specification of local queries. Assuming no lag, there is approximately a 0.1 second delay between additions.

#### Arguments

- `urls` – (Required) The multiline string of URLs to be [`stream`](#stream)ed, separated by ++enter++ keypresses

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? example

    Running

    ```
    ;batch_add
    Bohemian Rhapsody - Queen
    Billie Jean - Michael Jackson
    Hotel California - Eagles
    Sweet Child o' Mine - Guns N' Roses
    Rolling in the Deep - Adele
    ```

    will stream [ref] those songs in that order. Note that for longer lists, Discord will only allow the rapid sending of 5 messages at a time.

### [`clear`](#clear)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Clears all songs in queue.

This command does nothing if there are no songs in the queue. Clearing the queue does not do anything to a current playing song.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`current`](#current)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Shows the current song

The current song is the exact text word-for-word that was queried. If the current song cannot be retrieved, the query will be `None`.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`join`](#join)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Joins a voice channel

Also controls where bot messages are sent. Text output will be sent from the channel this command was run in. This command can be run multiple times safely.

#### Arguments

- `channels` – The name or id to the voice channel

### [`leave`](#leave)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Disconnects the bot from voice and clears the queue

In addition to clearing the queue, this command also erases all [global bot information](./additional.md#info_global).

### [`loop`](#loop)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Gets or sets queue looping

By default the queue is not set to loop. The user can set three types of looping options, specified by the `loop` argument:

- If `loop` = 0, no loop
- If `loop` > 0, loop all songs
- If `loop` < 0, loop one song

If no argument is passed, it shows the type of looping as either `0`, `1`, or `-1`.

#### Arguments

- `loop` – (Optional) An integer specifying the loop type

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`move`](#move)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Moves a song on queue

The playback queue is effectively 1-indexed. This means position 1 of the queue represents the first item in the queue, 2 the second item, and so on. The `move` command also supports negative indices where position -1 represents the last item in the queue, -2 the 2<sup>nd</sup> last item, etc.

When a song gets moved from `origin` to `target`, `origin`[^2] does not swap places with the song at `target`[^2]. Instead, `target` gets changed to `origin` and all songs after `target` gets pushed back one position.

[^2]: Starting from here until the end of this paragraph References of `origin` and `target` refer to "song at `origin`" and "song at `target`" respectively.

#### Arguments

- `origin` – The position in queue of the song to be moved
- `target` – The position in queue in which the moved song will occupy

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`pause`](#pause)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Pauses playing

Pausing the voice client. This command can be used multiple times.

#### Before Invoking Conditions

- Bot must be in the process of playing something

### [`queue`](#queue)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Shows the songs on queue

The first line of the queue specifies size as well as the type of [`loop`](#loop).

If there are no songs in the queue, the next line will be `None`.

If there are songs in the queue, this command outputs and numbers them from 1 to the total queue size. Each item in the queue is the exact song query that the user specified with the [`stream`](#stream) command.

If the queue exceeds the discord message limit size, it will be printed as multiple messages.

#### Before Invoking Conditions

- Bot must be connected to voice channel

### [`remove`](#remove)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Removes a song on queue

Likewise to [`move`](#move), the `remove` command accepts both positive and negative positions. After removal, songs below the removed song are then shifted up one position to accommodate for the gap.

#### Arguments

- `position` – The position of the song in the queue to be removed

#### Before Invoking Conditions

- Bot must be connected to voice channel

### [`resume`](#resume)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Resumes playing

Resumes the voice client to play the paused song. This command can be used repeatedly.

#### Before Invoking Conditions

- Bot must be in the process of playing something

### [`shuffle`](#shuffle)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Shuffles the queue

The shuffle process is to randomly scramble the order of the songs in queue. Queue stays the same if there are 0 or 1 songs in the queue.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`skip`](#skip)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Skips current song

Stops playing of the current song, which in turn causes the automatic fetching of the next song, which depends on the looping condition.

If no loop is set on the queue, skipping causes the current song to be removed from the queue.

Skipping a paused song does not persist the pause for the next song.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? warning

    Having this command run in quick succession is known to cause the bot to freeze on the current song. The usual way to resolve the bot freezing is to [reschedule](./additional.md#reschedule).

### [`stream`](#stream)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Plays from a url (almost anything yt-dlp supports)

Places the url to be streamed in the queue if a current song is playing. Plays[^4] the url's stream if this command is used is nothing is playing.

[^4]: It actually forces a scheduled advancement of the queue. See [reschedule](./additional.md#reschedule) and the [dev log](./devlog.md) for more information.

The "url" specified doesn't have to a url specifically. It can be any text query to be searched (on YouTube under normal usage). To be technical, "url" is the query passed into the yt-dlp `URL` argument.

This command also supports the following special queries:

- `prev`: Queries the previously played song and adds it to the queue if **it exists** and it was **added with this command or [`;stream_prepend`](./additional.md#stream_prepend)** (is a streamed query)
- `cur`: Queries the currently playing song and adds it to the queue if **it exists** and it was **added with this command or [`;stream_prepend`](./additional.md#stream_prepend)** (is a streamed query)

This command also supports the addition of links with embeds hidden by the `<>`.

The query must be printable[^3] and not longer than 100 characters.

#### Arguments

- `url` – The song query (that gets fetched as a streamable link)

#### Before Invoking Conditions

- Either user or bot must be connected to a voice channel

[^3]:  Put simply, it should be safely displayed and printed as human-readable text. Click <a href="https://docs.python.org/3/library/string.html#string.printable" target="_blank">here</a> for more information.

??? tip

    Sometimes a song might exist on one site but not in another. To specify a song to be played on SoundCloud for example, one can do:

    ```
    ;stream scsearch: damper float
    ```

    to search SoundCloud for the song "damper float" instead of YouTube, simply by specifying the `scsearch:` prefix.

    If no prefix is specified as with normal usage of the command, it defaults to searching YouTube.

    A list of supported prefixes can be found <a href=https://github.com/ytdl-patched/ytdl-patched/blob/ytdlp/supportedsites.md target="_blank">here</a>.

??? example

    YouTube query:
    ```
    ;p SZA - Kill Bill
    ```

    YouTube link (Laura Brehm - Parallel):
    ```
    ;p https://www.youtube.com/watch?v=kWVNbXvIpxU
    ```

    YouTube livestream (will bring up a livestream most of the time):
    ```
    ;p Lofi Girl livestream
    ```

    SoundCloud query:
    ```
    ;p scsearch: Snail's House Pixel Galaxy
    ```

    SoundCloud link without embed (elmo & Nico Harris - Mirage (feat. Israel Strom)):
    ```
    ;p <https://soundcloud.com/radiojuicy1/elmo-nico-harris-mirage>

    ```

    Other link (10 Hours of Vinyl - That Diggin’ Show Complete S03):
    ```
    ;p https://vimeo.com/248460715
    ```

    Play previous song:
    ```
    ;p prev
    ```

    Play current song:
    ```
    ;p cur
    ```

    Explicity search for the "prev" query:
    ```
    ;p ytsearch: prev
    ```

### [`volume`](#volume)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Gets or changes the player's volume

Volume of the bot defaults to 100% for each new song played. The volume applied only persists for the duration of the current playing song.

The bot is able to set the volume from 0% to 200%, thereore allowing for slight amplification.

If the `volume` argument is not specified, then this command displays the volume of the current song.

#### Arguments

- `volume` – (Optional) The volume to set the bot to play at

#### Before Invoking Conditions

- Bot must be connected to a voice channel
