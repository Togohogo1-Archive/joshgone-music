---
title: Playlist Management
---

## Overview

This bot also provides very basic playlist functionality[^1]. Playlists here are simply stored as plaintext and are given a name.

[^1]: Playlists are implemented this way for legacy reasons

The first two playlist commands are the [`;check`](#check) command and the [`;playlists`](#playlists) command

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;check`](#check) `<name>` | `;h1` | 1s | Output the text for a single playlist |
| [`;playlists`](#playlists) | `;li` | 1s | Configure playlists |

The [`;playlists`](#playlists) command may be followed by a subcommand to form `;playlists subcommand` that acts like a normal command. Some [`;playlists`](#playlists) subcommands:

| Command with Arguments[^1] | Aliases | Cooldown | Description |
|-|-|-|-|
| [`;playlists add`](#add) `<name>` `<text>` | `;li add` | 5s | Add a playlist |
| [`;playlists find`](#find) `<name_pattern>` | `;li find` | 1s | Find playlists whose names contain or match the given pattern |
| [`;playlists owner`](#owner) `<name>` `[new_owner]` | `;li owner` | 1s | Check or set the owner of a playlist |
| [`;playlists remove`](#remove) `<name>` | `;li remove` | 1s | Remove a playlist |
| [`;playlists rename`](#rename) `<name>` `<new_name>` | `;li rename` | 1s | Rename a playlist |
| [`;playlists search`](#search) `<name_pattern>` `[max_amount]` | `;li search` | 1s | Find playlists whose contents contain or match the given pattern |
| [`;playlists update`](#update) ... | | | |

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

### [`playlists`](#playlists)

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

??? example

    The command

    ```
    ;playlists add myplaylist
    ## My Playlist

    ### Jazz
    - "Autumn Leaves" by Miles Davis
    - "Take Five" by Dave Brubeck
    - "So What" by Miles Davis

    ### Rock
    - "Stairway to Heaven" by Led Zeppelin
    - "Bohemian Rhapsody" by Queen
    - "Hotel California" by Eagles

    ### Pop
    - "Shape of You" by Ed Sheeran
    - "Happy" by Pharrell Williams
    - "Uptown Funk" by Mark Ronson ft. Bruno Mars
    ```

    Will result in nicely rendered Discord output when `;check myplaylist` is run:

    <h2>My Playlist</h2>

    <h3>Jazz</h3>
    <ul>
      <li>"Autumn Leaves" by Miles Davis</li>
      <li>"Take Five" by Dave Brubeck</li>
      <li>"So What" by Miles Davis</li>
    </ul>

    <h3>Rock</h3>
    <ul>
      <li>"Stairway to Heaven" by Led Zeppelin</li>
      <li>"Bohemian Rhapsody" by Queen</li>
      <li>"Hotel California" by Eagles</li>
    </ul>

    <h3>Pop</h3>
    <ul>
      <li>"Shape of You" by Ed Sheeran</li>
      <li>"Happy" by Pharrell Williams</li>
      <li>"Uptown Funk" by Mark Ronson ft. Bruno Mars</li>
    </ul>

### [`find`](#find)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Find playlists whose names contain or match the given pattern

The find command uses basic [glob](https://research.swtch.com/glob) matching and operates on the name of the playlist. In addition to normal alphanumeric characters and underscore special characters supported are ? and %, for matching one and any number of characters respectively.

This command returns the number of playlists found that satisfy the given pattern along with their names, listed in alphabetical order. If none are found, it simply returns a list of 0 playlist with output `None`.

#### Arguments

- `name_pattern` – The character (glob) patten to match playlist names against

??? example

    Assume the following playlists exist (if these commands are run in series):
    ```
    %playlists add amogus   -
    %playlists add amoguise -
    %playlists add mongus   -
    %playlists add mongue   -
    ```

    Usage:
    ```
    %playlists find amogus  -> amogus           (exact match)
    %playlists find amo%    -> amogus, amoguise (prefix)
    %playlists find %gus    -> amogus, mongus   (suffix)
    %playlists find mongu?  -> mongus, mongue   (any character)
    %playlists find %m?gu%e -> amoguise         (combine them)
    %playlists find gui     -> amoguise         ("gui" in amoguise)
    ```

### [`owner`](#owner)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Check or set the owner of a playlist

To check the owner of a playlist, run this command without specifying the `new_owner` argument.

To change a playlist's owner, either the playlist must have no owner, or you are the bot owner, guild owner, or the playlist owner.

To clear the owner, pass `-` as the new owner.

#### Arguments

- `name` – The name of the playlist
- `new_owner` – (Optional) The nickname, handle, ID of a Discord user or a `-` to indicate no owner

??? warning

    If anyone in the server has the nickname `-`, then this command cannot be used to set ownership using that nickname. You have to use their Discord handle or Discord ID instead.

??? Example

    ```
    %playlists owner playlist             ->  gets the playlist's current owner
    %playlists owner playlist phibiscool  ->  make phibiscool the playlist owner
    %playlists owner playlist -           ->  removes the playlist's owner
    ```

### [`remove`](#remove)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Remove a playlist

A user may only remove a playlist if they are the bot owner, server owner, the playlist owner, or if the playlist has no owner.

#### Arguments

- `name` – The name of the playlist

### [`rename`](#rename)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Rename a playlist

A user may only rename a playlist if they are the bot owner, server owner, playlist owner, or if they playlist has no owner.

The constraints for the new playlist name follows the same guidelines as the [add](#add) command.

Additionally, a playlist cannot be renamed to itself or an existing playlist name.

#### Arguments

- `name` – The name of the playlist
- `new_name` – The new name of the playlist

### [`search`](#search)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Find playlists whose contents contain or match the given pattern

This command functions exactly the same as [`;find`](#find) but it acts on the chant contents rather than the chant names.

Searching through chant contents might take a while, so there is an optional parameter that only returns the first `max_amount` chants (in alphabetical order) in which the substring or glob-ish pattern to search for matches the playlist contents.

#### Arguments

- `name_pattern_` – Substring or glob-ish pattern match to find in playlist contents
- `max_amount` – (Optional) The maximum number of playlists to return

### [`update`](#update)

## Owner Only Subcommands

### [`regexfind`](#regexfind)

### [`regexremove`](#regexremove)

### [`regexsearch`](#regexsearch)
