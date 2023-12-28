---
title: Developer Features
---

## Overview

This section contains an overview of commands located in `jgm/extensions/admin.py` and `jgm/extensions/database.py`. Which are owner-only commands that interface more closely with the bot's code.

Additionally, this section also contains information on tools the bot offers that developers might find useful, like a REPL or database management details.

Since these commands are not meant to be used by the average user, there is no point in having an alias or cooldown.

First, common administrative commands:

| Command with Arguments | Description |
|-|-|
| [`;ctx_`](#adminctx_) | Adds a context instance to the bot |
| [`;extensions`](#adminextensions) | Lists all loaded extensions |
| [`;load`](#adminload) `<module>` | Loads an extension/cog |
| [`;reload`](#adminreload) `<module>` | Reloads an extension/cog |
| [`;shutdown`](#adminshutdown) | Shuts the bot down |
| [`;unload`](#adminunload) `<module>` | Unloads an extension/cog |
| [`;reinit`](#databasereinit) | Reinitializes the bot for a server |

## Admin Commands

### [`admin.ctx_`](#adminctx_)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v2.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Adds a context instance to the bot

Adding a [context](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=discord%20ext%20commands%20context%20context#context) instance to the global [bot](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#bot) object requires manually running this command, which is useful for debugging in the [REPL](#the-repl).

### [`admin.extensions`](#adminextensions)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Lists all loaded extensions

Those that are loaded on startup are:

- `jgm.extensions.admin`
- `jgm.extensions.playlists`
- `jgm.extensions.music`
- `jgm.extensions.database`
- `jgm.extensions.info`
- `jgm.extensions.repl`[^1]

[^1]: See the [REPL](#the-repl) section

### [`admin.load`](#adminload)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Loads an extension/cog

Loads with the [`load_extension`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=load_extension#discord.ext.commands.Bot.load_extension) coroutine function.

#### Arguments

- `module` – The extension/cog

### [`admin.reload`](#adminreload)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Reloads an extension/cog

Reloads with the [`reload_extension`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=load_extension#discord.ext.commands.Bot.reload_extension) coroutine function.

This is almost the same as an unload followed by a load. See the [`reload_extension`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=load_extension#discord.ext.commands.Bot.reload_extension) documentation for more information.

#### Arguments

- `module` – The extension/cog

??? note

    Running `;reload admin` on the bot will work, but running `;unload admin` followed by `;load admin` will not.

### [`admin.shutdown`](#adminshutdown)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Shuts the bot down

### [`admin.unload`](#adminunload)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v1.0.0</a>
</sup>

Unloads an extension/cog

Unloads with the [`unload_extension`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=load_extension#discord.ext.commands.Bot.reload_extension) coroutine function.

#### Arguments

- `module` – The extension/cog

### [`database.reinit`](#databasereinit)

<sup>
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Initial Release">:octicons-rocket-24: v1.0.0</a>&nbsp;&nbsp;&nbsp;
<a href="https://github.com/Togohogo1/joshgone-music/releases/tag/v1.0.0" target="_blank", title="Latest Update">:octicons-tag-24: v2.0.0</a>
</sup>

Reinitializes the bot for a server

To maintain the functionality of commands that require database reading like the [`;playlist`](./playlists.md) commands, the server (guild) ID must exist under the `server` TABLE in the `jgmusic.db` database file.

This command removes the current server the bot is in from the table (or does nothing if it doesn't exist), and adds it back in, thereby "reinitializing" it.

## Database Information

## The REPL

All the bot's functionality can be replicated via command line. On startup, the REPL cog is loaded only if the `JGM_REPL` environment variable is set to 1.
