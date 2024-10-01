import numpy as np
from scipy.io import wavfile
import src.utils as utils
from collections import OrderedDict

SAMPLING_RATE = 44100
DURATION_SECONDS = 5
MAX_AMPLITUDE = 2**13


class Timeline:
    def __init__(self, *, duration_seconds, sampling_rate):
        self.duration_seconds = duration_seconds
        self.sampling_rate = sampling_rate
        self.timeline = np.linspace(
            0, duration_seconds, num=sampling_rate * duration_seconds
        )

    def __str__(self) -> str:
        return f"Timeline(duration_seconds={self.duration_seconds}, sampling_rate={self.sampling_rate})"


class TimelineFactory:
    """
    This class is a factory for creating Timeline objects. It caches the created Timeline objects

    cache is a dictionary that maps (duration_seconds, sampling_rate) to Timeline objects
    """

    # to avoid memory leak, limit the cache size
    CACHE_SIZE = 10**6

    cache = OrderedDict()

    @classmethod
    def get_timeline(cls, *, duration_seconds, sampling_rate):
        # check for cache hit
        if (
            duration_seconds,
            sampling_rate,
        ) in cls.cache:
            return cls.cache[
                (duration_seconds, sampling_rate)
            ]

        # create a new timeline object and add it to the cache
        timeline = Timeline(
            duration_seconds=duration_seconds, sampling_rate=sampling_rate
        )
        cls.cache[
            (duration_seconds, sampling_rate)
        ] = timeline

        # if the cache is full, remove the first item
        if len(cls.cache) > cls.CACHE_SIZE:
            cls.cache.popitem(last=False)

        return timeline


class SoundWave:
    """
    Class to represent a sound wave.

    Creating an underlying sound wave array is done eagerly in the constructor.

    Homework task a "method to print any details you think will be important about the wave"
    is implemented in the __str__ method, not in a SoundWaveFactory class.
    """

    def __init__(self, *, timeline, note, amplitude):
        self.note = note
        self.amplitude = amplitude
        self.timeline = timeline

        self.sound_wave = utils.get_soundwave(
            timeline=self.timeline, note=self.note, amplitude=self.amplitude
        ).astype(np.int16)

    def __str__(self) -> str:
        return f"SoundWave(note={self.note}, amplitude={self.amplitude}, timeline={self.timeline})"


class SoundWaveFactory:
    """
    Factory class for creating SoundWave objects.

    Similar to TimelineFactory, this class caches the created SoundWave objects.

    Cached tuples are large, but I think caching is still good because attributes like
    sampling_rate, amplitude, and duration_seconds are common across many SoundWave objects, and 
    the memory will not be increased by much.

    The cache is limited to CACHE_SIZE to avoid memory leaks

    """

    # lru cahce of tuples (sampling_rate, note, amplitude, duration_seconds) to SoundWave objects

    CACHE_SIZE = 10**6

    cahe = OrderedDict()

    def __init__(
        self,
        *,
        sampling_rate,
        default_duration_seconds,
        max_amplitude,
        timeline_factory=None,
    ):
        self.sampling_rate = sampling_rate
        self.default_duration_seconds = default_duration_seconds
        self.max_amplitude = max_amplitude
        if timeline_factory is None:
            self.timeline_factory = TimelineFactory()

    def create_note(self, note="a4", name=None, duration_seconds=None, amplitude=None):
        if duration_seconds is None:
            duration_seconds = self.default_duration_seconds
        if amplitude is None:
            amplitude = self.max_amplitude
            
        sound_wave = self.__get_from_cache_or_add(duration_seconds, note, amplitude)
        
        return sound_wave
        

    def __get_from_cache_or_add(self, duration_seconds, note, amplitude):
        
        # check for cache hit
        if (
            self.sampling_rate,
            note,
            amplitude,
            duration_seconds,
        ) in self.cahe:
            return self.cahe[
                (self.sampling_rate, note, amplitude, duration_seconds)
            ]

        #  create timeline object
        timeline = self.timeline_factory.get_timeline(
            duration_seconds=duration_seconds, sampling_rate=self.sampling_rate
        )
        
        # create a new sound wave object and add it to the cache
        sound_wave = SoundWave(
            timeline=timeline, note=note, amplitude=amplitude
        )

        self.cahe[
            (self.sampling_rate, note, amplitude, duration_seconds)
        ] = sound_wave

        # if the cache is full, remove the first item
        if (
            len(self.cahe)
            > self.CACHE_SIZE
        ):
            self.cahe.popitem(
                last=False
            )

        return sound_wave


# get_normed_sin = lambda timeline, frequency: MAX_AMPLITUDE * np.sin(
#     2 * np.pi * frequency * timeline
# )
# get_soundwave = lambda timeline, note: get_normed_sin(timeline, NOTES[note])
# common_timeline = np.linspace(0, DURATION_SECONDS, num=SOUND_ARRAY_LEN)


# def create_note(note="a4", name=None, timeline: np.dtype("float64") = common_timeline):
#     sound_wave = get_soundwave(timeline, note).astype(np.int16)
#     if name is None:
#         file_name = f"{note}_sin.wav".replace("#", "s")
#     else:
#         file_name = f"{name}.wav"
#     wavfile.write(file_name, SAMPLING_RATE, sound_wave)
#     return sound_wave


# if __name__ == "__main__":
#     a4 = create_note()
#     np.savetxt(
#         "a4_sin.txt", a4
#     )  # https://numpy.org/doc/stable/reference/routines.io.html
