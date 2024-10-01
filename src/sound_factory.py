import numpy as np
import src.utils as utils
from collections import OrderedDict
from scipy.io import wavfile


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

    Cache is a dictionary that maps (duration_seconds, sampling_rate) to Timeline objects
    """

    # to avoid memory leak, limit the cache size
    CACHE_SIZE = 10**6

    cache = OrderedDict()

    @classmethod
    def get_timeline(cls, *, duration_seconds, sampling_rate):
        # check for cache hit
        cache_key = cls.__get_cache_key(
            duration_seconds=duration_seconds, sampling_rate=sampling_rate
        )

        if cache_key in cls.cache:
            return cls.cache[cache_key]

        # create a new timeline object and add it to the cache
        timeline = Timeline(
            duration_seconds=duration_seconds, sampling_rate=sampling_rate
        )
        cls.cache[cache_key] = timeline

        # if the cache is full, remove the first item
        if len(cls.cache) > cls.CACHE_SIZE:
            cls.cache.popitem(last=False)

        return timeline

    @staticmethod
    def __get_cache_key(*, duration_seconds, sampling_rate):
        return (duration_seconds, sampling_rate)


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
            timeline=self.timeline.timeline, note=self.note, amplitude=self.amplitude
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

    # Probably enum is another good option for this
    SAVE_TYPE_TXT = "TXT"
    SAVE_TYPE_WAV = "WAV"

    def __init__(
        self,
        *,
        sampling_rate,
        default_duration_seconds,
        max_amplitude,
        timeline_factory=None,
    ):
        """
        param: sampling_rate: int: the sampling rate of the sound wave. Once set, you can not use the same
        factory to create sound waves with different sampling rates.

        param: default_duration_seconds: float: the default duration of the sound wave in seconds.
        when you call create_wave without specifying the duration, this value will be used.

        param: max_amplitude: int: the maximum amplitude of the sound wave. It is default amplitude
        at the same time. You should not call create_wave with amplitude greater than this value.

        param: timeline_factory: TimelineFactory: the factory to create Timeline objects. If None, a new
        TimelineFactory object will be created.
        """

        self.sampling_rate = sampling_rate
        self.default_duration_seconds = default_duration_seconds
        self.max_amplitude = max_amplitude
        if timeline_factory is None:
            self.timeline_factory = TimelineFactory()

    def get_soundwave(self, note="a4", duration_seconds=None, amplitude=None):
        """
        This function creates a SoundWave object with the given note, duration, and amplitude.

        This is the similar function to create_note from the original SoundWaveFactory class.
        I did not like the name create_note, so I changed it to create_wave.

        Also, I moved the functionality of creating a txt and wav file to other functions.
        """

        if duration_seconds is None:
            duration_seconds = self.default_duration_seconds
        if amplitude is None:
            amplitude = self.max_amplitude

        return self.__get_from_cache_or_add(duration_seconds, note, amplitude)

    def save_wave(self, sound_wave, file_name=None, type=SAVE_TYPE_TXT):
        """
        a method to save wave into np.array txt by default and into WAV file if parameter "type='WAV'" is provided

        Do not provide the file extension or directory path in the file_name parameter, just the file name.
        extension is automatically txt or wav

        All txt files are saved in the "sound_text_files" folder in the root directory, and all wav files are saved
        in the "sound_wav_files" folder in the root directory.

        Name of

        :raises ValueError: if type parameter is not 'TXT' or 'WAV'

        """

        file_name = self.__generate_file_name(sound_wave, file_name, type)
        if type == self.SAVE_TYPE_TXT:
            np.savetxt(file_name, sound_wave.sound_wave)
        elif type == self.SAVE_TYPE_WAV:
            wavfile.write(file_name, self.sampling_rate, sound_wave.sound_wave)
        else:
            raise ValueError("type parameter should be 'TXT' or 'WAV'")


    def normalize_sound_waves(self, sound_waves):
        """
        a method to normalize_sound_waves several waves: in both length (to the shortest file) and amplitude (according to the amplitude attribute)

        I decided to use average amplitude and the shortest wave to normalize all sound waves.
        I hope this was meant by the task.
        """

        # find the average amplitude and the shortest wave
        average_amplitude = sum([sound_wave.amplitude for sound_wave in sound_waves]) / len(sound_waves)
        shortest_wave = min(sound_waves, key=lambda sound_wave: len(sound_wave.sound_wave))
        
        # create a new list of normalized sound waves
        normalized_sound_waves = []
        
        for sound_wave in sound_waves:
            new_sound_duration = len(shortest_wave.sound_wave)
            new_amplitude = average_amplitude
            new_sound_wave = self.get_soundwave(sound_wave.timeline, sound_wave.note, new_amplitude)
            normalized_sound_waves.append(new_sound_wave)
        
        return normalized_sound_waves

    def __generate_file_name(self, sound_wave, file_name, type):
        # default name is sound_wave_note_duration_seconds_amplitude
        if not file_name:
            file_name = f"sound_wave_{sound_wave.note}_{sound_wave.timeline.duration_seconds}_{sound_wave.amplitude}"

        if type == self.SAVE_TYPE_TXT:
            return f"sound_text_files/{file_name}.txt".replace("#", "s")
        elif type == self.SAVE_TYPE_WAV:
            return f"sound_wav_files/{file_name}.wav".replace("#", "s")
        else:
            raise ValueError("type parameter should be 'TXT' or 'WAV'")

    
    
    

    def __get_from_cache_or_add(self, duration_seconds, note, amplitude):
        """
        just a helper function
        """

        # check for cache hit
        cache_key = self.__get_cache_key(
            duration_seconds=duration_seconds, note=note, amplitude=amplitude
        )
        if cache_key in self.cahe:
            return self.cahe[cache_key]

        #  create timeline object
        timeline = self.timeline_factory.get_timeline(
            duration_seconds=duration_seconds, sampling_rate=self.sampling_rate
        )

        # create a new sound wave object and add it to the cache
        sound_wave = SoundWave(timeline=timeline, note=note, amplitude=amplitude)

        self.cahe[cache_key] = sound_wave

        # if the cache is full, remove the first item
        if len(self.cahe) > self.CACHE_SIZE:
            self.cahe.popitem(last=False)

        return sound_wave

    def __get_cache_key(self, *, duration_seconds, note, amplitude):
        # I separated cache key function to avoid bugs and make the code more readable
        return (self.sampling_rate, note, amplitude, duration_seconds)
