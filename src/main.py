from src.sound_factory import SoundWaveFactory


SAMPLING_RATE = 44100
DURATION_SECONDS = 5
MAX_AMPLITUDE = 2**13


if __name__ == "__main__":
    sound_factory = SoundWaveFactory(
        default_duration_seconds=DURATION_SECONDS,
        max_amplitude=MAX_AMPLITUDE,
        sampling_rate=SAMPLING_RATE,
    )

    a4 = sound_factory.get_soundwave(note="a4", amplitude=MAX_AMPLITUDE)

    print(a4)
