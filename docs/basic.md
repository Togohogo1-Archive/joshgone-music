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

[^1]: `[optinal argument] <required arguiment>`

## Commands

Recategorize them later

### [`batch_add`](#batch_add)

Plays from multiple URLs split by lines.

Splits the URLs by appropriate line termination character and individually [`stream`](#stream)s [ref] each query. Does not support specification of local queries. Assuming no lag, there is approximately a 0.1 second delay between additions.

**Arguments**

- `urls` – (Required) The multiline string of URLs to be [`stream`](#stream)ed, separated by ++enter++ keypresses

**Before Invoking Behaviour**

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

**Before Invoking Behaviour**

- Bot must be connected to a voice channel

### [`current`](#current)

Shows the current song

The current song is the exact text word-for-word that was queried. If the current song cannot be retrieved, the query will be `None`.

**Before Invoking Behaviour**

- Bot must be connected to a voice channel

### `join`

### `leave`

### `loop`

### `move`

### `pause`

### `queue`

### `remove`

### `resume`

### `shuffle`

### `skip`

### `stream`

### `volume`