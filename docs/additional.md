---
title: Additional Features
---

## Overview

The table below summarizes extra commands for more advanced bot usage. Click on any of them for more details, including special use cases, caveats, etc:

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;apply_filter`](#apply_filter) `<filter_name>` | `;f` | 1s | Applies a filter to the next song |
| [`;autoshuffle`](#autoshuffle) `[to_ashuffle]` | `;ashuffle` | 1s | Gets or sets queue autoshuffler status |
| [`;cancel`](#cancel) | | 1s | Cancels an existing sleep timer |
| [`;daycore`](#daycore) | `;dc` | 1s | Applies the daycore effect |
| [`;fast_forward`](#fast_forward) `[sec]` | `;ff` | 0.5s | Seeks a short amount of time forward into a song |
| [`;forceskip`](#forceskip) | `;fs` | 1s | Skips a song and removes it from the queue |
| [`;info`](#info) | `;i` | 1s | Shows audio, metadata, and progress bar information for current song |
| [`;info_global`](#info_global) | `;ig` | 1s | Shows music information that doesn't get reset for each song |
| [`;jump`](#jump) `<pos>` | `;j` | 2s | Jumps to a timestamp in the song |
| [`;nightcore`](#nightcore) | `;nc` | 1s | Applies the nightcore effect |
| [`;normal`](#normal) | `;no` | 1s | Resets current effects and filters |
| [`;pitch`](#pitch) `<factor>` | `;pi` | 1s | Changes the pitch of a song |
| [`;playback_history`](#playback_history) `[display_last]` | `;history`, `;hist` | 1s | Outputs the playback history |
| [`;playback_history_clear`](#playback_history_clear) | `;hclear` | 1s | Clears the playback history |
| [`;playlist_link`](#playlist_link) `<url>` | | 3s | Adds all songs in a playlist to the queue |
| [`;playlist_link`](#playlist_link) `<url>` | | 3s | Adds all songs in a playlist to the queue |
| [`;rewind`](#rewind) `[sec]` | `;rr` | 0.5s | Seeks a short amount of time backwards into the song |
| [`;sleep_in`](#sleep_in) `[dur]` | `;leavein`, `;sleepin` | 1s | Makes the bot automatically leave the voice channel after some time |
| [`;speed`](#speed) `<factor>` | `;sp` | 1s | Changes the tempo of a song |
| [`;stream_prepend`](#stream_prepend) `<url>` | | 1s | Plays from a url (almost anything yt-dlp supports) and places it at the beginning of the queue |

And some additional owner-only commands:

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;local`](#local) `<query>` | | 1s | Plays a file from the local filesystem |
| [`;local_prepend`](#local_prepend) `<query>` | | 1s | Plays a file from the local filesystem and places it at the beginning of the queue |
| [`;reschedule`](#reschedule) | |  | Reschedules the current guild onto the advancer task |

[^1]: `[optinal argument] <required arguiment>`

## Commands

Recategorize them later

### [`apply_filter`](#apply_filter)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Applies a filter to the next song

The definition of "filter" here refers to any distortion of the audio source such that the speed does not change and the overall pitch doesn't change.

Applying a specific filter affects all subsequent songs until a new filter is applied.

The filter for the current song cannot be changed while the song is playing.

Here is a table of the currently available filters:

|Filter name | Description |
|-|-|
|`bassboost`| Amplifies the bass of the song |
|`default`| No filter |
|`deepfry`| Low quality sound with intentional amplifiation of all frequencies to the extreme |

#### Arguments

- `filter_name` – Name of the filter to apply (see "Filter name" column)

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`autoshuffle`](#autoshuffle)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Gets or sets queue autoshuffler status

Randomly shuffles the queue once every 5 seconds if on.

If no arguments are provided, then this command simply prints if the autoshuffler is on or off.

#### Arguments

- `to_ashuffle` – (Optional) A boolean value (True/False) representing the state of the autoshuffler

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`cancel`](#cancel)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Cancels an existing sleep timer

Deactivates the sleep timer's task of automatically leaving the voice channel after a period of time, if there is a task running.

Forcing the bot to [`leave`](./basic.md#leave) the voice channel forces a cancel.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`daycore`](#daycore)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Applies the daycore effect, opposite of [`nightcore`](#nightcore)

In terms of this bot, an *effect* is defined as a pitch change or a tempo change in the song.

The daycore effect is achieved by applying a 20% decrease in tempo and pitch. This effect is common enough to warrant its own command for ease of usage.

When run, the daycore effect will be applied to the next song played.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`fast_forward`](#fast_forward)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Seeks a short amount of time forward into a song

If no argument is specified, this command defaults to seeking forward 5 seconds. Otherwise, the amount of seconds seeked forward must be an integer in between 1 and 15.

Fast forwarding when a speed effect is applied makes no difference from fast forwarding on 1x speed. This command will seek to the same location given the same starting point of a song for any tempo.

If the specified seek time goes beyond the end of the song, this command will move forward by the remaining time until the end of the song.

#### Arguments

- `sec` – (Optional, Default = 5) The amount of seconds to seek forward into the current song. Limited from 1 to 15 seconds.

#### Before Invoking Conditions

- Bot must be in the process of playing something

??? warning

    For an unspecified reason (most likely due to latency), fast forwarding on [streamed](./basic.md#stream) audio longer than ~15 minutes tends to cause delays. See this Stack Overflow <a href="https://stackoverflow.com/questions/74972819/discord-py-music-bot-slowing-down-for-longer-audio-queries" target="_blank">post</a> for more details.

    Slight buffering may also be noticeable when running this command while the tempo of the song is slower than normal.

    Executing this command extremely quickly in succession may cause the bot to freeze on the current song, which is usually resolved with a [reschedule](#reschedule).

### [`forceskip`](#forceskip)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Skips a song and removes it from the queue

Forceskip is a more advanced version of skip. It allows "forcefully" skipping songs that are currently playing. When a song is forcefully skipped, it gets removed from the queue which means that even if the queue is looping, the forceskipped song will not reappear again.

This command uses the [`reschedule`](#reschedule) command behind the scenes in a way such that it is more resilient to spamming.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`info`](#info)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Shows audio, metadata, and progress bar information for current song

The very first line upon running this command will show the direct query that the user made to queue the song.

Next, two tables outlining audio and metadata information:

=== "Metadata Info"

    | Field | Description <small>(if applicable)</small> |
    |-|-|
    | `DOMAIN` | Name of the website which the query was taken from |
    | `ID` | The query URL's unique identifier |
    | `LINK` | Direct link to the query URL |
    | `TITLE` | Title retrieved from the query URL. Usually more complete than the actual query. |
    | `UPLOADER` | User who was responsible for uploading/curating the query URL |

=== "Audio Info"

    | Field | Description <small>(if applicable)</small> |
    |-|-|
    | `EFFECTS` | The tempo and pitch being used for the currently playing song, formatted `x# speed, x# pitch`. See [`speed`](#speed) and [`pitch`](#pitch) for more details.|
    | `FILTER` | The filter being used for the currently playing song. See [`apply_filter`](#apply_filter) for more details. |
    | `VOLUME` | The volume of the currently playing sone. See [`volume`](./basic.md#volume) for more details.|

A progress bar keeps track how far into the song one is, acting like a playhead. To the right of the progress bar includes the total time into the song and the duration of the entire song.

If the song is a livestream, then a `(live)` will be there to indicate so, the total time of the song will be `00:00:00`. Time into the song will still be tracked normally. In addition, `(paused)` will be shown if the song is paused.

The metadata information will be different for songs added locally. That is, whatever <a href="https://mutagen.readthedocs.io/en/latest/" target="_blank">mutagen</a> is able to extract from the local audio file.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? warning

    The progress bar/seek head showing total time into the song will be slightly in accurate for longer songs. The longer the song the more inaccurate. For most cases, this inaccuracy is negligible.

??? example

    ``` text title="Sample Command Output"
    ;stream pink floyd

    DOMAIN   youtube.com
    ID       k9ynZnEBtvw
    LINK     https://www.youtube.com/watch?v=k9ynZnEBtvw
    TITLE    Pink Floyd - The Dark Side Of The Moon (50th Anniversary) [2023 Remaster] {Full Album}
    UPLOADER Pink Floyd

    EFFECTS  x0.8 speed, x0.8 pitch
    FILTER   default
    VOLUME   100.0%

    [#######.............] 00:15:08/00:42:56
    ```

### [`info_global`](#info_global)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Shows music information that generally doesn't get reset for each song

The basic command description explains why this command has the name "global". These global features are outlined in the following table:

| Field | Description |
|-|-|
|`AUTOSHUFFLE_TASK`| Indicates if the autoshuffler is on or not. Takes on values of `running` and `None`. See [`autoshuffle`](#autoshuffle) for more details. |
|`NEXT_EFFECTS`| The effects that will be applied to the next song. In the form of `x# speed, x# pitch`. See [`speed`](#speed) and [`pitch`](#pitch) for more details. |
|`NEXT_FILTER`| The filter that will be applied to the next song. See [`apply_filter`](#apply_filter) for more details. |
|`HISTORY_SIZE`| Minimum of the total number of songs played and 100, the maximum size of the playback history queue. See [`playback_history`](#playback_history) for more details|
|`LOOP_TYPE`| Describes if the queue is looping or not (and the type of loop if it is). See [`loop`](./basic.md#loop) for more details.|
|`PAUSED`| `True`/`False`, if the bot is paused. |
|`PLAYING`| `True`/`False`, if the bot is playing. |
|`PROCESSING`| JoshGone Music internal state for music advancing. Takes on `True`/`False`. See this [page](./jgmusic.md) for more information.|
|`QUEUE_LENGTH`| Number of songs in the queue. |
|`SLEEP_TIMER_TASK`| Indicates if a sleep timer is on ir not. Takes on values of `running` and `None`. See [`sleep_in`](#sleep_in) for more details. |
|`SONGS_PLAYED`| Number of songs that have been played so far. Includes those skipped manually or from error. |
|`WAITING`| JoshGone Music internal state for music advancing. Takes on `True`/`False`. See this [page](./jgmusic.md) for more information.|

This command may be run as long as the bot is connected to a voice channel.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? example

    ``` text title="Sample Command Output"
    AUTOSHUFFLE_TASK running
    GLOBAL_EFFECTS   x1.2 speed, x1.2 pitch
    GLOBAL_FILTER    default
    HISTORY_SIZE     10
    LOOP_TYPE        no loop
    PAUSED           False
    PLAYING          False
    PROCESSING       False
    QUEUE_LENGTH     0
    SLEEP_TIMER_TASK None
    SONGS_PLAYED     10
    WAITING          False
    ```

### [`jump`](#jump)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Jumps to a timestamp in the song

The timestamp `<pos>` (as specified below) can be specified in terms of number of seconds or `[HH:[MM:]]SS`. The latter means that seconds are always mandatory, then followed by minutes and hours.

Seconds alone can range from 0 to 359999. If seconds is used as part of the latter form, then it only goes up to 59. The same happens with minutes. Hours can go up to 99.

Jumping is possible when the current song is paused and does not automatically resume the song when done. Jumping also preserves things like volume, filters, and effects.

If jumped further than the current song's length, the song gets skipped.

#### Arguments

- `pos` – The timestamp to jump to. Either in seconds or `[[HH;]MM:]SS` format.

#### Before Invoking Conditions

- Bot must be in the process of playing something

??? warning

    Jumping to further locations be slightly in accurate for longer songs. The longer the song the more inaccurate. For most cases, this inaccuracy is negligible.

??? example

    Jump to 1 minute and 30 seconds

    ```
    ;j 1:30
    ```

    Jump to 1 minute and 30 seconds

    ```
    ;j 90
    ```

    Jump to 1 hour and 30 seconds

    ```
    ;j 1:30:00
    ```

    Jump to 99 hours and 59 minutes

    ```
    ;j 99:59:00
    ```

    Jump to 5 minutes

    ```
    ;j 5:00
    ```

    Jump to 1 second less than 10 minutes

    ```
    ;j 9:59
    ```

    Jump to the maximum time allowed

    ```
    ;j 99:59:59
    ```

    Jump to the maximum time allowed

    ```
    ;j 359999
    ```

    Jump to the beginning of a song

    ```
    ;j 0
    ```

### [`nightcore`](#nightcore)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Applies the nightcore effect, opposite of [`daycore`](#daycore)

In terms of this bot, an *effect* is defined as a pitch change or a tempo change in the song.

The nightcore effect is achieved by applying a 20% increase in tempo and pitch. This effect is common enough to warrant its own command for ease of usage.

When run, the nightcore effect will be applied to the next song played.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`normal`](#normal)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Resets current effects and filters

Changes will be applied to the next song. To be specific, sets the tempo to x1, pitch to x1, and the filter to `default`.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`pitch`](#pitch)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Changes the pitch of a song

A change in pitch is applying an *effect*. The definition of *effect* is a pitch or tempo change to the song. Changes are applied to the next song.

A value for the pitch `factor` that isn't a power of 2 (not x0.25, x0.5, x1, x2, x4) will shift the key of the song.

#### Arguments

- `factor` – The factor in which to change the pitch by. Limited between x0.25 to x4.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? warning

    This command requires FFmpeg to be compiled with <a href="https://ffmpeg.org/ffmpeg-filters.html#rubberband" target="_blank">librubberband</a>.

### [`playback_history`](#playback_history)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Outputs the playback history

This command displays a maximum of 100 songs but keeps track of the total number of songs plays.
The names of the items in the playback history are the direct queries that the user made.

If the specified number of songs to include in playback history output includes all the songs ever played by the bot, the total songs played counter will not be displayed.

Songs in the playback history outputs are numbered 1 to `display_last`. The smaller the number, the more recently played it was.

This command will notify the user if there is no playback history. If output is too long, the bot will send multiple messages.

#### Arguments

- `display_last` – (Optional, Default = 5) Display last `display_last` songs played

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`playback_history_clear`](#playback_history_clear)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Clears the playback history

In addition to clearing the playback history, it also resets the number of songs played. If the bot leaves the voice channel, the playback history gets automatically cleared.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`playlist_link`](#playlist_link)

<sup> <a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp; <a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
:octicons-beaker-24: Experimental
</sup>

Adds all songs in a playlist to the queue

A playlist is any online collection of songs that yt-dlp is able to support. It essentially loops through all the songs in the playlist and adds them in via [`;stream`](./basic.md#stream). These songs are usually links.

Wrapping the playlist link with angle brackets (`<>`) wraps all links in the playlist in brackets, effectively preventing individual links to show an embed (like when running the [`;current`](./basic.md#current) command).

This command has only been tested for YouTube and SoundCloud playlists:

- YouTube playlists are formatted like `https://www.youtube.com/playlist?list=<id>`
- SoundCloud playlists are formatted like `https://soundcloud.com/<user>/sets/<playlist>`

#### Arguments

- `url` – Link to the online playlist

#### Before Invoking Conditions

- Either user or bot must be connected to a voice channel

??? example

    Running this command:

    ```
    ;playlist_link <https://www.youtube.com/playlist?list=PLocQeghkorOWXJ3tu8YwNfbwjxTJ2UZWV>
    ```

    And then `;queue` immediately after should output:

    ```
    Queue [56] (no loop):
    1: <https://www.youtube.com/watch?v=z-ys_60gmEE>
    2: <https://www.youtube.com/watch?v=edpbsFvypK0>
    3: <https://www.youtube.com/watch?v=clVx1bccHpU>
    4: <https://www.youtube.com/watch?v=osRSZaCswds>
    5: <https://www.youtube.com/watch?v=-uH2_sPJuLw>
    6: <https://www.youtube.com/watch?v=wdCbjTSQwn4>
    7: <https://www.youtube.com/watch?v=P3UguXUvECM>
    8: <https://www.youtube.com/watch?v=WTaABER2IgI>
    9: <https://www.youtube.com/watch?v=vMbGOlMvmFU>
    10: <https://www.youtube.com/watch?v=ubd3IRnogAk>
    11: <https://www.youtube.com/watch?v=saZ0ZKE8sdo>
    12: <https://www.youtube.com/watch?v=qD54sROmeIM>
    13: <https://www.youtube.com/watch?v=SySHO4W00fs>
    14: <https://www.youtube.com/watch?v=BoNDM-0PMjM>
    15: <https://www.youtube.com/watch?v=UiOAyrrtbOs>
    16: <https://www.youtube.com/watch?v=aup_iSqqAXE>
    17: <https://www.youtube.com/watch?v=elAG4FsjkuA>
    18: <https://www.youtube.com/watch?v=wSRAdi1wVW0>
    19: <https://www.youtube.com/watch?v=tDOla8ZFVKo>
    20: <https://www.youtube.com/watch?v=XORwfYUH23Y>
    21: <https://www.youtube.com/watch?v=U7v2e_piJUc>
    22: <https://www.youtube.com/watch?v=rBU8wRCnaUM>
    23: <https://www.youtube.com/watch?v=R-kmPds0KSM>
    24: <https://www.youtube.com/watch?v=wmmj7Giie6g>
    25: <https://www.youtube.com/watch?v=Uc7567tTjOw>
    26: <https://www.youtube.com/watch?v=LCdWr3Zrt5s>
    27: <https://www.youtube.com/watch?v=_VDR2eLwtpo>
    28: <https://www.youtube.com/watch?v=gADlgxrnAdQ>
    29: <https://www.youtube.com/watch?v=QVhkyh5OYSU>
    30: <https://www.youtube.com/watch?v=N_ILB4bQsLA>
    31: <https://www.youtube.com/watch?v=zeCwfZWNt70>
    32: <https://www.youtube.com/watch?v=BVP65Rg8myE>
    33: <https://www.youtube.com/watch?v=Qc11_jkOKx0>
    34: <https://www.youtube.com/watch?v=9N4airsRCV0>
    35: <https://www.youtube.com/watch?v=WsWkLVi2Xf8>
    36: <https://www.youtube.com/watch?v=foaw2arHA50>
    37: <https://www.youtube.com/watch?v=wu0I5h6wG34>
    38: <https://www.youtube.com/watch?v=E8e19xlb7mM>
    39: <https://www.youtube.com/watch?v=I4VD4OwUhDw>
    40: <https://www.youtube.com/watch?v=1qVrPtq2tcg>
    41: <https://www.youtube.com/watch?v=pt6R-_-aEzY>
    42: <https://www.youtube.com/watch?v=5y1lp540t_c>
    43: <https://www.youtube.com/watch?v=--uwRamO3ws>
    44: <https://www.youtube.com/watch?v=prNruaG9iDA>
    45: <https://www.youtube.com/watch?v=aC4H7o53Ng4>
    46: <https://www.youtube.com/watch?v=l03BFd3wDaE>
    47: <https://www.youtube.com/watch?v=KsReWI83IC8>
    48: <https://www.youtube.com/watch?v=13wdFhH34Ms>
    49: <https://www.youtube.com/watch?v=-wbSvwa9hQk>
    50: <https://www.youtube.com/watch?v=h66Ys4BXCU8>
    51: <https://www.youtube.com/watch?v=dmzuBBu-O7Q>
    52: <https://www.youtube.com/watch?v=ZhIs6rUn7Pg>
    53: <https://www.youtube.com/watch?v=3grkLm0pabA>
    54: <https://www.youtube.com/watch?v=uDcpSJIdx5g>
    55: <https://www.youtube.com/watch?v=kszjdpUF0Js>
    56: <https://www.youtube.com/watch?v=aSRHJmNJuQU>
    ```

    This playlist contains YouTube links to all songs from the Cuphead OST.

??? warning

    When adding a SoundCloud playlist with more than 5 songs, the 6<sup>th</sup> song and beyond will be an API link in the format of `https://api-v2.soundcloud.com/tracks/<track_id>`. The first 5 songs will be how they are normally displayed as an online link.

### [`rewind`](#rewind)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Seeks a short amount of time backwards into the song

If no argument is specified, this command defaults to seeking backward 5 seconds. Otherwise, the amount of seconds seeked backward must be an integer in between 1 and 15.

Rewinding when a speed effect is applied makes no difference from fast forwarding on 1x speed. This command will seek to the same location given the same starting point of a song for any tempo.

Unlike [`;fast_forward`](#fast_forward), only a certain amount of time may be seeked backward, and this amount of time depends on the current playback speed:

- ~15 seconds for x0.25 speed
- 75 seconds for x1 speed
- nearly 5 minutes for 4x speed

This is because the bot caches some of the raw audio that gets played and this difference in speed keeps the size of this cache consistent for different playback speeds.

If the rewind time goes beyond what the cache can store or the beginning of the song, this command will truncate the rewind time to a value less than what was specified.

#### Arguments

- `sec` – (Optional, Default = 5) The amount of seconds to seek backward into the current song. Limited from 1 to 15 seconds.

#### Before Invoking Conditions

- Bot must be in the process of playing something

### [`sleep_in`](#sleep_in)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Makes the bot automatically leave the voice channel after some time

More specifically, this command creates a sleep timer. Once the timer counts down to 0, the bot will automatically leave the voice channel. There can be only one sleep timer running at a time, and sleep timers operate on a server-level.

If the argument `dur` is not specified, then this command will show if a sleep timer is running and how much time it will take for the bot to disconnect from the voice channel. This time may not be super accurate due to some Discord latency.

If specifying the `dur` argument, please refer to the [`;jump`](#jump) command for a description on how to format it.

Once the bot leaves the voice channel, all the information specified in [`;info`](#info) and [`;info_global`](#info_global) will be reset.

#### Arguments

- `dur` – (Optional) Time until the bot leaves the voice channel. Either in seconds or `[[HH;]MM:]SS` format.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`speed`](#speed)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Changes the tempo of a song

A change in tempo is applying an *effect*. The definition of *effect* is a pitch or tempo change to the song. Changes are applied to the next song.

When this effect is applied to a song, the relative time of the song is kept constant. This means that doing [`;fast_foward`](#fast_forward)s and [`;rewind`](#rewind)s will result in the same start and end seek positions no matter what the tempo may be. Another way to think about this is if:

- `factor` > 1, then it will take less than 10 seconds for the song to reach the 10 second timestamp shown in [`;info`](#info)
- `factor` < 1, then it will take more than 10 secods for the song tor each 10 second timestamp shown in [`;info`](#info)

#### Arguments

- `factor` – The factor in which to change the tempo by. Limited between x0.25 to x4.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

??? warning

    This command requires FFmpeg to be compiled with <a href="https://ffmpeg.org/ffmpeg-filters.html#rubberband" target="_blank">librubberband</a>.

### [`stream_prepend`](#stream_prepend)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Plays from a url (almost anything yt-dlp supports) and places it at the beginning of the queue

Exact same as [`;stream`](./basic.md#stream) but when placing the song into the queue, it places it in the beginning rather than the end. A prepended song placed in the queue will be played next provided no autoshuffler is active.

#### Arguments

- Exact same as [`;stream`](./basic.md#stream)

#### Before Invoking Conditions

- Exact same as [`;stream`](./basic.md#stream)

## Owner Only

### [`local`](#local)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
:octicons-beaker-24: Experimental
</sup>

Plays a file from the local filesystem

The bot that anything added with this command will be fetched form the local filesystem. Songs on the local filesystem may be in a variety of common audio formats (`.mp3`, `.wav`, `.ogg`, etc.)[^2].

[^2]: This command supports all audio formats that <a href="https://mutagen.readthedocs.io/en/latest/" target="_blank">Mutagen</a> supports

Like the [`;stream`](./basic.md#stream) command, `;local` places the query in the queue as a local type if a current song is playing. It plays the from the file if nothing is playing. *Play* here means reading the raw data from the audio file.

This command also supports the following special queries:

- `prev`: Queries the previously played song and adds it to the queue if **it exists** and it was **added with this command or [`;local_prepend`](#local_prepend)** (is a local query)
- `cur`: Queries the currently playing song and adds it to the queue if **it exists** and it was **added with this command or [`;local_prepend`](#local_prepend)** (is a local query)

This command also supports the addition of links with embeds hidden by the `<>`.

Although there is no length limit on local file paths, their sizes will be naturally limited by the user's operating system.

#### Arguments

- `query` – The local file path to the song

#### Before Invoking Conditions

- Either user or bot must be connected to a voice channel

### [`local_prepend`](#local_prepend)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
:octicons-beaker-24: Experimental
</sup>

Plays from a url (almost anything yt-dlp supports) and places it at the beginning of the queue

Exact same as [`;local`](#local) but when placing the song into the queue, it places it in the beginning rather than the end. A prepended song placed in the queue will be played next provided no autoshuffler task is active.

#### Arguments

- Same as [`;local`](#local)

#### Before Invoking Conditions

- Same as [`;local`](#local)

### [`reschedule`](#reschedule)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
</sup>

Reschedules the current guild onto the advancer task

When playing audio, sometimes something unexpected happens and the bot chokes up and gets stuck in the middle of a song with no way to [`;skip`](./basic.md#skip). Compared to restarting and rejoining, invoking this command is the least destructive way to fix this issue. In other words, it forcefully restarts the queue advancement loop.

For an in-depth explanation, see this [page](./jgmusic.md).

#### Before Invoking Conditions

- Bot must be connected to a voice channel
