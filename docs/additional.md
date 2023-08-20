---
title: Additional Features
---

## Overview

The table below summarizes extra commands for more advanced bot usage. Click on any of them for more details, including special use cases, caveats, etc.

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;apply_filter`](#apply_filter) `<filter_name>` | | 1s | Applies a filter to the next song |

## Commands

Recategorize them later

### [`apply_filter`](#apply_filter)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v2.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Applies a filter to the next song

The definition of "filter" here refers to any distortion of the audio source such that the speed does not change and the overall pitch doesn't change.

Applying a specific filter affects all subsequent songs until a new filter is applied.

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

### `autoshuffle`

### `cancel`

### `daycore`

### `fast_forward`

### `forceskip`

### `info`

### `info_global`

### `jump`

...

Does not cause resume

### `nightcore`

### `normal`

### `pitch`

### `playback_history`

### `playback_history_clear`

### `playlist_link`

### `rewind`

### `sleep_in`

### `speed`

### `stream_prepend`

## Owner Only

### `local`

### `local_prepend`

### `reschedule`
