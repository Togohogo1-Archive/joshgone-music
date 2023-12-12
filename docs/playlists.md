---
title: Playlist Management
---

## Overview

This bot also provides very basic playlist functionality[^1]. Playlists here are simply stored as plaintext and are given a name.

[^1]: Playlists are implemented this way for legacy reasons

The first two playlist commands are the [`;check`](#check) command and the [`;playlist`](#playlist) command

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;check`](#check) `<name>` | `;h1` | 1s | Output the text for a single playlist |
| [`;playlist`](#playlist) | `;li` | 1s | Configure playlists |

The [`;playlist`](#playlist) command may be followed by a subcommand to form `;playlist subcommand` that acts like a normal command. Some [`;playlist`](#playlist) subcommands:

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;playlist add`](#add) `<name>` `<text>` | `;li add` | 5s | Add a playlist |
| [`;playlist check`](#check) ... | | | |
| [`;playlist find`](#find) ... | | | |
| [`;playlist list`](#list) ... | | | |
| [`;playlist owner`](#owner) ... | | | |
| [`;playlist remove`](#remove) ... | | | |
| [`;playlist update`](#update) ... | | | |

And some owner-only subcommands

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;playlist regexfind`](#add) ... | | | |
| [`;playlist regexremove`](#add) ... | | | |
| [`;playlist regexsearch`](#add) ... | | | |

## Commands

### [`check`](#check)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Output the text for a single playlist

The playlist must exist in the list of playlists

#### Arguments

- `name` – The name of the playlist

### [`playlist`](#playlist)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Configure playlists

If not followed by a subcommand, this command simply prints out the number of playlists and their names in alphabetical order. If there exists 0 playlists, then it prints `None`.

See the following section [Subcommands](#subcommands) for usage of this command in such a way.

## Subcommands

### [`add`](#add)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Add a playlist

This command will fail if a playlist with the same name already exists. Playlists can be stored as multiline text blocks with Discord formatting. Playlists are stored as plaintext and cannot be executed directly via a command.

Playlists also must only contain alphanumeric characters + underscore, and the maximum number of playlists that can be stored is 500 with each playlist not being able to exceed 35 characters in length.

#### Arguments

- `name` – The name of the playlist
- `text` – The contents of the playlist

??? Example

    The command

    ```
    ;playlists add myplaylist
    # My Playlist

    ## Jazz
    - "Autumn Leaves" by Miles Davis
    - "Take Five" by Dave Brubeck
    - "So What" by Miles Davis

    ## Rock
    - "Stairway to Heaven" by Led Zeppelin
    - "Bohemian Rhapsody" by Queen
    - "Hotel California" by Eagles

    ## Pop
    - "Shape of You" by Ed Sheeran
    - "Happy" by Pharrell Williams
    - "Uptown Funk" by Mark Ronson ft. Bruno Mars
    ```

    Will result in nicely rendered Discord output when `;check myplaylist` is run:

    # My Playlist

    ## Jazz
    - "Autumn Leaves" by Miles Davis
    - "Take Five" by Dave Brubeck
    - "So What" by Miles Davis

    ## Rock
    - "Stairway to Heaven" by Led Zeppelin
    - "Bohemian Rhapsody" by Queen
    - "Hotel California" by Eagles

    ## Pop
    - "Shape of You" by Ed Sheeran
    - "Happy" by Pharrell Williams
    - "Uptown Funk" by Mark Ronson ft. Bruno Mars

### [`find`](#find)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

### [`owner`](#owner)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

### [`remove`](#remove)

### [`rename`](#remove)

### [`search`](#remove)

### [`update`](#update)

## Owner Only Subcommands

### [`regexfind`](#regexfind)

### [`regexremove`](#regexremove)

### [`regexsearch`](#regexsearch)
