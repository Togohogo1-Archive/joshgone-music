---
title: How JG Music Works
---

*The information may be useful for future developers looking to dig more into the inner working of the bot and for my own reference. Understanding this section requires knowledge on Python's `asyncio` library.*

## Flowchart

(write this last) To ensure a working queueing system that works across servers, JG Music uses a somewhat complicated music advancing method with status flags. The most important process of JGMusic (the core) is the music advancing system
The music advancement process in short, ensures that once a song finishes playing, the next one gets played right after. (maybe come back to this later too)

The following flowchart depicts a high-level overview of the music advancing system, including a small section on what happens during [`load`]()s/[`unload`]()s.

All flowchart nodes are labelled with a number to be elaborated further on in the next sections.

```mermaid
graph TD
    subgraph "Normal Function"
    Z(["(1) Start"]) --> A["(2) On initialize"];
    A --> B["(3) <code>self.advancer.start</code>"];
    B --> C["(4) Create <code>handle_advances</code> task"];
    C --> G["(5) Wait for <code>advance_queue.get</code>"]
    D["(6) Play song"] --> E["(7) <code>schedule</code>"];
    E --> F["(8) <code>advance_queue.put_nowait</code>"];
    F --> G
    G --> H["(9) Received <code>(ctx, error)</code>"];
    H --> I["(10) Create a <code>handle_advance</code> task"];
    I --> J["(11) Do the advance handling"];
    J -->|"<code>after=after<code>"| E;
    end
    subgraph "Loading and Unloading"
    B --> a{"(1) <code>;unload music</code>"};
    a -->|no| B;
    a -->|yes| b["(2) <code>cog_unload</code>"];
    b --> d["(3) <code>on_advancer_cancel</code>"];
    c["(4) <code>;load music</code>"] --> A;
    end
```

## Normal Function in Detail

??? note

    Mentions of `music.py`, `self`, or `Music` will refer to the file `jgm/extensions/music`, unless stated otherwise.

### (1) Start

The entry point of JG Music is `jgmusic.py`. When `hatch run jgm` is executed in the terminal, a series of functions are called which eventually leads to `jgm/extensions/music.Music.setup` which is a special discord.py function that executes when an extension gets loaded with [`load_extension`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=load_extension#discord.ext.commands.Bot.load_extension):

### (2) On initialize

Initialization refers to the instantiation of the `Music` cog, which happens when `Music.setup` calls `return bot.add_cog(Music(bot))`. The bot enters this state on startups and loads, which is covered [below](#4-load-music).

### (3) `self.advancer.start`

There exists the `bot` object and the `Music` cog. `Music` may be unloaded but `bot` will be available at all times. An `asyncio.Queue` object is stored in the `bot` and a copy is stored in `Music`. An `asyncio.Task` object `self.advance_task` is also stored in `Music` and is by default `None`.

At the very end of the `__init__` function in `Music`, `self.advancer.start` is called, which eventually [starts](https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html?highlight=start#discord.ext.tasks.Loop.start) the advancer in the event loop. `Music.advancer` is a `discord.ext.tasks.Loop` object that runs once every 15 seconds to see if an `self.advance_task` can be created. If there is an issue (`self.advance_task` will be done), this function auto-restarts the `self.advance_task` advancer.

### (4) Create `handle_advances` task

If `self.advance_task` is `None`, it will be set to an `asyncio.Task` (`asyncio.create_task` wrapped) `Music.handle_advances()` coroutine, otherwise known as the **music_advancer**.

This gets put in the global `asyncio` event loop and eventually runs "soon".

### (5) Wait for `advance_queue.get`

Inside the `Music.handle_advances()` coroutine is an infinite loop that first `await`s an item from `self.advance_queue` (pauses its execution until it receives the queued item).

### (6) Play song

The way to play a song involves invoking the following commands

- `;stream`
- `;stream_prepend`
- `;local`
- `;local_prepend`
- `;playlist_link`

or directly as Python code from the [REPL](./dev.md#the-repl).

Each of these commands trigger the `self.schedule` function from `Music`.

### (7) Schedule

### (8) `advance_queue.put_nowait`

### (9) Received `(ctx, error)`

Continuing from [(6)](#6-play-song), the coroutine resumes execution after an item is obtained. This item is a tuple:

- The first element `ctx` is an `discord.ext.commands.context.Context` object
- The second element `error` is a player error that happened sometime before handling an advance.

Having a `discord.ext.commands.context.Context` object useful for fetching the user who ran the command, along with the server they are currently in, along with a lot of other useful information. This allows one `asyncio.Queue` to be used to manage multiple bot "instances" in many servers.

Player errors are quite rare under normal usage of the bot. However, the most common one is

```text
Player error: OSError(10038, 'An operation was attempted on something that is not a socket', None, 10038, None)
```

Technically, the code is completely functional if the second element was removed. It is kept for clarity and ease of debugging.

### (10) Create a `handle_advance` task

### (11) Do the advance handling

## Loading and Unloading in Detail

### (1) `;unload music`

### (2) `cog_unload`

### (3) `on_advancer_cancel`

### (4) `;load music`

## Extra Notes

### `asyncio.sleep(1)`
