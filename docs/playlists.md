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
| [`;playlist add`](#add) ... | | | |
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

### [`playlist`](#playlist)

## Subcommands

### [`add`](#add)

### [`check`](#check)

### [`find`](#find)

### [`list`](#list)

### [`owner`](#owner)

### [`remove`](#remove)

### [`update`](#update)

## Owner Only Subcommands

### [`regexfind`](#regexfind)

### [`regexremove`](#regexremove)

### [`regexsearch`](#regexsearch)
