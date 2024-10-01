from src.sound_factory import SoundWaveFactory


SAMPLING_RATE = 44100
DURATION_SECONDS = 5
MAX_AMPLITUDE = 2**13


def save_a4_as_text_and_sound():
    sound_factory = SoundWaveFactory(
        default_duration_seconds=DURATION_SECONDS,
        max_amplitude=MAX_AMPLITUDE,
        sampling_rate=SAMPLING_RATE,
    )

    a4 = sound_factory.get_soundwave(note="a4", amplitude=MAX_AMPLITUDE)

    sound_factory.save_wave(a4, "a4", type=SoundWaveFactory.SAVE_TYPE_WAV)
    sound_factory.save_wave(a4, "a4", type=SoundWaveFactory.SAVE_TYPE_TXT)

if __name__ == "__main__":
    save_a4_as_text_and_sound()