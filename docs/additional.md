---
title: Additional Features
---

## Overview

The table below summarizes extra commands for more advanced bot usage. Click on any of them for more details, including special use cases, caveats, etc.

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

[^1]: `[optinal argument] <required arguiment>`

## Commands

Recategorize them later

### [`apply_filter`](#apply_filter)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Cancels an existing sleep timer

Deactivates the sleep timer's task of automatically leaving the voice channel after a period of time, if there is a task running.

Forcing the bot to [`leave`](./basic.md#leave) the voice channel forces a cancel.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`daycore`](#daycore)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Skips a song and removes it from the queue

Forceskip is a more advanced version of skip. It allows "forcefully" skipping songs that are currently playing. When a song is forcefully skipped, it gets removed from the queue which means that even if the queue is looping, the forceskipped song will not reappear again.

This command uses the [`reschedule`](#reschedule) command behind the scenes in a way such that it is more resilient to spamming.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`info`](#info)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
|`PROCESSING`| JoshGone Music internal state for music advancing. Takes on `True`/`False`. See this [page](./devlog.md) for more information.|
|`QUEUE_LENGTH`| Number of songs in the queue. |
|`SLEEP_TIMER_TASK`| Indicates if a sleep timer is on ir not. Takes on values of `running` and `None`. See [`sleep_in`](#sleep_in) for more details. |
|`SONGS_PLAYED`| Number of songs that have been played so far. Includes those skipped manually or from error. |
|`WAITING`| JoshGone Music internal state for music advancing. Takes on `True`/`False`. See this [page](./devlog.md) for more information.|

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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Resets current effects and filters

Changes will be applied to the next song. To be specific, sets the tempo to x1, pitch to x1, and the filter to `default`.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`pitch`](#pitch)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Changes the pitch of a song

A change in pitch is applying an *effect*. The definition of *effect* is a pitch or tempo change to the song. Changes are applied to the next song.

A non-integer value for the pitch `factor` will shift the key of the song.

#### Arguments

- `factor` – The factor in which to change the pitch by. Limited between x0.25 to x4

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`playback_history`](#playback_history)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;
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

### `playback_history_clear`

### `playlist_link`

- one of the less developed commands, still in experimental phase

### `rewind`

- mention the buffer
- only can seek back a certain amount of time

### `sleep_in`

- there can be only one sleep timer running at a time
- the sleep timer operates server-wide

### `speed`

- Talk about how relative time is kept constant here?
- Also point towards the librubberband warning

### `stream_prepend`

## Owner Only

### `local`

- experimental (tag for it?)

### `local_prepend`

- experimental (tag for it?)

### `reschedule`

- experimental (tag for it?)
