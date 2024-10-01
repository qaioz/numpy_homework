from src.sound_factory import SoundFactory
import numpy as np


if __name__ == "__main__":
    sound_factory = SoundFactory()
    a4 = sound_factory.create_note()
    np.savetxt("a4_sin.txt", a4)
    print(a4)
