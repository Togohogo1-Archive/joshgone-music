---
title: How JG Music Works
---

*The information may be useful for future developers looking to dig more into the inner working of the bot and for my own reference.*

Understanding this section requires an understanding of how Python's asyncio works.

(maybe write this last)

To ensure a working queueing system that works across servers, JG Music uses a somewhat complicated music advancing method with status flags.

---

The entry point of JG Music is `joshgone.py`. At this point, the extensions are loaded in. This section will focus on `music.py`'s music advancement process.

The music advancement process in short, ensures that once a song finishes playing, the next one gets played right after. (maybe come back to this later too)

(rename this to not joshgone.py later)

`jgmusic.py` calls its `main()` function, which leads to a series of calls until the `_run()` function which does the necessary setup to startup the bot. Here the `music.py` extension gets loaded.

``` mermaid
graph TD
  A[<code>Start</code>] --> B{Error?};
  B -->|Yes| C[Hmm...];
  C --> D[Debug];
  D --> B;
  B ---->|No| E[Yay!];
```
