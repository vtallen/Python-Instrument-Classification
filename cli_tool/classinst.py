import os
import sys
import pickle

from dataset_gen.converttowav import tester_func

__USAGE__ = 'python3 classinst.py <audiofile>'\
        'python3 classinst.py -m <model.pkl> <audiofile>'

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    # Case in which a model is supplied
    if argc == 4:
        model_filename = argv[2]
        audio_filename = argv[3]
        pass
    elif argc == 2:
        pass
    else:
        print(__USAGE__)
        sys.exit(1)
