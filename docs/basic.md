---
title: Basic Features
---

# Basic Features

## Overview

The table below summarizes all the commands for basic bot usage. Click on any of them for more details, including special use cases, caveats, etx.

| Command | Aliases | Arguments[^1] | Cooldown | Description |
|-|-|-|-|-|
| [`;batch-add`](#batch_add) |  | `<urls>` | 2s | Plays from multiple URLs split by lines |
| [`;clear`](#clear)    |  |  | 1s | Clears all songs in queue |
| [`;current`](#current)   | `;c` |  | 0.5s | Shows the current song |
| [`;join`](#join)   |  | `<channel>` | 1s | Joins a voice channel |
| [`;leave`](#leave)   |  |  | 1s | Disconnects the bot from voice and clears the queue |
| [`;loop`](#loop)   |  | `[loop]` | 1s | Gets or sets queue looping |
| [`;move`](#move)   |  | `<origin> <target>` | 1s | Moves a song on queue |
| [`;pause`](#pause)   | `;stop` | | 0.5s | Pauses playing |
| [`;queue`](#queue)   | `;q` | | 1s | Shows the songs on queue |
| [`;remove`](#remove)   |  | `<position>` | 1s | Removes a song on queue |
| [`;resume`](#resume)   | `;start` | | 0.5s | Resumes playing |

[^1]: `[optinal argument] <required arguiment>`

## Commands

Recategorize them later

### [`batch_add`](#batch_add)

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

Clears all songs in queue.

This command does nothing if there are no songs in the queue. Clearing the queue does not do anything to a current playing song.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`current`](#current)

Shows the current song

The current song is the exact text word-for-word that was queried. If the current song cannot be retrieved, the query will be `None`.

#### Before Invoking Conditions

- Bot must be connected to a voice channel

### [`join`](#join)

Joins a voice channel

Also controls where bot messages are sent. Text output will be sent from the channel this command was run in. This command can be run multiple times safely.

#### Arguments

- `channels` – The name or id to the voice channel

### [`leave`](#leave)

Disconnects the bot from voice and clears the queue

In addition to clearing the queue, this command also erases all [global bot information](./additional.md#info_global).

### [`loop`](#loop)

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

Pauses playing

Pausing the voice client. This command can be used multiple times.

#### Before Invoking Conditions

- Bot must be playing something

### [`queue`](#queue)

Shows the songs on queue

The first line of the queue specifies size as well as the type of [loop](#loop).

If there are no songs in the queue, the next line will be `None`.

If there are songs in the queue, this command outputs and numbers them from 1 to the total queue size. Each item in the queue is the exact song query that the user specified with the [stream](#stream) command.

If the queue exceeds the discord message limit size, it will be printed as multiple messages.

#### Before Invoking Conditions

- Bot must be connected to voice channel

### [`remove`](#remove)

Removes a song on queue

Likewise to [move](#move), the `remove` command accepts both positive and negative positions. After removal, songs below the removed song are then shifted up one position to accommodate for the gap.

#### Arguments

- `position` – (Required) The position of the song in the queue to be removed

#### Before Invoking Conditions

- Bot must be connected to voice channel

### [`resume`](#resume)

Resumes playing

Resumes the voice client to play the paused song. This command can be used repeatedly.

#### Before Invoking Conditions

- Bot must be playing something

### `shuffle`

### `skip`

### `stream`

### `volume`