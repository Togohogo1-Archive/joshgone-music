# TODO

## Uncategorized

## Goals for Future Versions

- [ ] Extra decorations
  - Typing indicator in channel
  - Disable "is live" feature
  - Command sorting (more vs filters)
- [ ] More filters
  - [ ] Bass boost
  - [ ] Vaporwave (reverb)
  - [ ] Radio
- [ ] More organized error messages
- [ ] ytdlp logs in a log file instead of terminal
- [ ] Make 2nd draft of messages to the user
- [ ] Inconsistency in error quotes (`ExtensionNotFound` vs `CommandNotFound` single & double quotes)
- [ ] `<>` not actually needed for optional arguments
- [ ] Update JGM envvars and db name
- [ ] Turn all emphasis '', "" to italics
- [ ] 1x vs x1 speed
- [ ] Not all changes reflect repo rename
- [ ] Still have text portions in help manual
- [ ] Specify any default params (max_remove = -1 or smth)
- [ ] Rename server to servers in migrations python file
- [ ] Fix dark mode for ERD database diagram thing
- [ ] Note about guild_join server table ;running command combo causing chants to work
- [ ] Options is single quote, before options is double quote
- [ ] `self.var` <- double check for consiststency (I forgot what this was)

## Low-priority Potential Code Breakers

- When `;ff` 15 for a long song, then do `;s` or other commands
- When `;jump` x:xx for a long song, then do other commands
- When `;batch_add` a bunch of songs, do a `;ff` when a current one is playing
- When `;batch_add` a bunch of songs, do a `;jump` x:xx when a current one is playing
- When `;jump` x:xx causes a large delay, change the ffmpeg settings
- Spamming `;reschedule`
- `;fs` and then `;s` outputs 2 queue empty, then stops outputting
- `;reschedule` command when there is only one song
- if a long local file path, then paginator breaks
- `;reschedule` when there is only one song left in the queue and it is not looping in any way
- Spamming `;ff` or `;s` causes the bot to freeze if advancer isn't forced
