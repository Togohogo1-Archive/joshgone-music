import argparse
import sys
import json

import soundit as s

def make_chunks(infos, **kwargs):
    """Generate chunks from note infos"""
    return s.chunked(make_sound(infos, **kwargs))

def make_sound(note_infos, *, settings, template, cache=None):
    """Generate a sound from note infos"""

    # Cached to be a tad bit faster (removes float conversion step)
    @s.lru_iter_cache(maxsize=16)
    def instrument_sound_at(instrument, note_index, length):
        if 13 <= instrument <= 16:
            # 13=sine, 14=square, 15=sawtooth, 16=triangle
            # Ignored because I'm too lazy to find their actual volume
            return
        if instrument == 41:
            # I don't know what instrument this is lol
            return
        chunks = instrument_chunks_at(instrument, note_index)
        volume = settings["volume"][instrument]
        yield from ((x+y)/2*volume for x, y in s.unchunked(chunks))

    # Cached so that we don't start up 2000 FFmpeg processes
    @s.lru_iter_cache(cache=cache)
    def instrument_chunks_at(instrument, note_index):
        filename = template.replace("<>", str(instrument))
        length = 60 / (settings["originalBpm"][instrument] * 2)
        start = (note_index - settings["min"][instrument] - 24) * length
        args = s.make_ffmpeg_section_args(filename, start, length)
        process = s.create_ffmpeg_process(*args)
        yield from s.chunked_ffmpeg_process(process)

    # Sort by when each note is played
    note_infos = sorted(note_infos, key=lambda info: info["time"])

    # Save some time
    len_note_infos = len(note_infos)

    # Mapping between note types (A5, F#3) to note indices (69, 42)
    note_indices = s.make_indices_dict()

    # State we need between points
    playing_sounds = {}  # Dictionary of sounds (constant insert and removal)
    remove_sound_keys = []  # Stack of sounds to be removed
    next_note_info_index = 0  # The index of the next sound

    # Loop until we break (we don't know how long the song is)
    for current in s.passed(None):

        # Add sounds that are ready to be played
        while (
            next_note_info_index < len_note_infos
            and note_infos[next_note_info_index]["time"] <= current
        ):
            note_info = note_infos[next_note_info_index]
            sound = instrument_sound_at(
                note_info["instrument"],
                note_indices[note_info["type"].lower()],
                note_info["length"],
            )
            # sound = s.volume(note_info["volume"], sound)
            playing_sounds[next_note_info_index] = sound
            next_note_info_index += 1

        # Add up all playing sounds to get the current point
        point = 0
        for note_info_index in playing_sounds:
            try:
                point += next(playing_sounds[note_info_index])
            except StopIteration:
                # Remove the sound later (can't remove while iterating)
                remove_sound_keys.append(note_info_index)

        # Remove keys flagged to be removed
        while remove_sound_keys:
            del playing_sounds[remove_sound_keys.pop()]

        # Break out if nothing is playing and there are no more sounds to play
        if not next_note_info_index < len_note_infos and not playing_sounds:
            break

        yield point

parser = argparse.ArgumentParser(
    description="Generates PCM 16-bit 48kHz sound from note infos in stdin.",
)
parser.add_argument(
    "--settings",
    default="oscollection/settings.json",
    help="path to Online Sequencer settings JSON file",
)
parser.add_argument(
    "--template",
    default="oscollection/<>.ogg",
    help="template to Online Sequencer audio files",
)

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.settings) as file:
        settings = json.load(file)
    infos = json.load(sys.stdin)
    chunks = make_chunks(
        infos,
        settings=settings,
        template=args.template,
    )
    for chunk in chunks:
        sys.stdout.buffer.write(chunk)
