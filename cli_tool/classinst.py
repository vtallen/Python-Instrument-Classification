import os
import sys
import pickle
import glob
from statistics import mode
import shutil

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
from scipy.io import arff

# Allow relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dataset_gen')) 
from converttowav import convert_to_wav #pyright: ignore 
from splitaudio import split_audiofile # pyright: ignore 
from normalizedb import normalize_audio #pyright:ignore 
from extractFreqARFF import create_arff # pyright: ignore 
from cleandata import clean_file # pyright : ignore

TEMP_DIR = 'audiotmp/'
SPLIT_LEN = 0.1
WAV_DIR = TEMP_DIR + 'wav/'
SPLIT_DIR = TEMP_DIR + 'split/'
NORMALIZE_DIR = TEMP_DIR + 'normalized/'
ARFF_DIR = TEMP_DIR + 'arff/'
NORMALIZE_DBFS = -20
NUM_HARMONICS = 32

__USAGE__ = 'python3 classinst.py <audiofile>'\
        'python3 classinst.py -m <model.pkl> <audiofile>'

def predict(model, arff_filename):
    data, meta = arff.loadarff(arff_filename)
    df = pd.DataFrame(data)
    
    df.columns = meta.names()

    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].str.decode('utf-8')

    # print('Data head')
    # print('=================================')
    # print(df.head(10))
    # print() 

    attrib = df.iloc[:, :-1].values

    predicted_insts = model.predict(attrib)
    print('Instrument is:', mode(predicted_insts))
    # for inst in predicted_insts:
    #     print(inst)


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    # Case in which a model is supplied
    if argc == 4:
        model_filename = argv[2]
        audio_filename = argv[3]

        wav_filename = convert_to_wav(audio_filename, WAV_DIR) 
        os.makedirs(SPLIT_DIR, exist_ok=True)

        split_audiofile(wav_filename, SPLIT_LEN, SPLIT_DIR)
        
        filenames = glob.glob(SPLIT_DIR + '/*.wav')
        os.makedirs(NORMALIZE_DIR, exist_ok=True)
        for filename in filenames:
            normalize_audio(filename, NORMALIZE_DIR[:-1], NORMALIZE_DBFS)
        
        # Analyze the audio file
        os.makedirs(ARFF_DIR, exist_ok=True) 
        create_arff(NORMALIZE_DIR, NUM_HARMONICS, 'dataset', ARFF_DIR) 
        
        # Clean up the arff file
        clean_file(ARFF_DIR + 'datasetRaw.arff', ARFF_DIR + 'datasetRaw.arff')

        # load the model
        with open(model_filename, 'rb') as f:
            model = pickle.load(f)
        
        predict(model, ARFF_DIR + 'datasetRaw.arff')

        # Cleanup
        shutil.rmtree(TEMP_DIR)
        
    elif argc == 2:
        pass
    else:
        print(__USAGE__)
        sys.exit(1)
