"""
Ideas for advanced commands

sleep timer (sleep in hh:mm:ss) or just raw seconds
- remove the sleep timer
- change the sleep timer

fast forward
- fast forward x seconds

rewind
- go backwards x seconds

goto
- go to hh:mm:ss
- use fast ff and rw if time difference is less than x minutes (set to 10?)
- seems like vlc android doesn't allow jumping to ms

shuffle
- shuffle

loop current song
- continuously play the current song

previous song
- store a queue of previously played songs?
- size of the queue configurable?
- or just be able to do one previous song

more detailed song info?
[on vlc]
- length
- file size
- 0:00/5:00
- bitrate
- codec
- sample rate

playback speed
- a value between 0.25 to 4
- ^ if thats too laggy then do 0.5 to 2
- will be applied on next song

Equalizer
- gain for 10? diff audio frequencies?
- easy ffmpeg setting

Filters
- preset, some examples include:
- nightcore
- daycore
- bass boost
- vaporwave (reverb)
- radio
- will require complete redesign of _DEFAULT_FFMPEG_OPTS

ABrepeat
- continuously play the song from start_time to end_time without any lag
- only use with fast seeking type
- cancel abrepeat

forceskip
- skips the song and YEETS it from the queue

playlist support
-


features that might not be implemented
===============
- stop after some track
- browse parent (does this imply view filesystem)
- song bookmarking (play this bookmark -> song x at 1:25)
- the ability to sort tracks?
- playback history

"""