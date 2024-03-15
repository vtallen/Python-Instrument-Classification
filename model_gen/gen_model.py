import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
from scipy.io import arff

import pickle
import os
import sys
import glob

MODELS_DIR = 'models/'

def train_model(arff_filename, enabled_instruments = ['all']):
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

    if enabled_instruments != ['all']:
        df = df[df['instrument'].isin(enabled_instruments)]
        # df = df[~df['instrument'].isin(['AG', 'flute', 'piano'])]

    attrib = df.iloc[:, :-1].values
    instrument = df.iloc[:, -1].values
    
    X_train, X_test, y_train, y_test = train_test_split(attrib, instrument, test_size=0.25, random_state=0)

    classifier = DecisionTreeClassifier(random_state=0, min_samples_leaf=25)
    # classifier = DecisionTreeClassifier(criterion='entropy', random_state=1029, min_samples_leaf=25)

    classifier.fit(X_train, y_train)

    y_predict = classifier.predict(X_test)

    matrix = confusion_matrix(y_test, y_predict)
    matrix_labels = sorted(set(y_test) | set(y_predict))
    matrix_df = pd.DataFrame(matrix, index=matrix_labels, columns=matrix_labels) # type: ignore
    print('Filename:', arff_filename)
    print('Enabled instruments:', enabled_instruments)
    print('=================================')
    print()
    print('Confusion matrix:')
    print('=================================')
    print(matrix_df)
    print()

    accuracy = accuracy_score(y_test, y_predict)
    print('Accuracy score:')
    print('=================================')
    print(accuracy)
    print()
    
    ossplit = os.path.split(arff_filename)
    name, extension = os.path.splitext(ossplit[1])

    # Save the model as an object file that can be loaded back into sklearn
    if not os.path.exists(MODELS_DIR):
        os.mkdir(MODELS_DIR)

    with open(MODELS_DIR + '/' + name + "Model.pkl", 'wb') as f:
        pickle.dump(classifier, f)
    
    # Create a bytestring of the model so that it can be directly embedded into a script
    # Using w instaed of wb to write it as something I can just dump into another script straight from the txt file 
    with open(MODELS_DIR + '/' + name + 'ByteStr' + '.txt', 'w') as f:
        byte_str = pickle.dumps(classifier)
        f.write('MODEL=')
        f.write(str(byte_str))
    
__USAGE__ = 'python3 gen_model.py <datasets> <outdir> ... - where <datasets> is a directory containing arff files and <outdir> is where to save models. ... is a space seperated list of the instruments to enable in the model'

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    
    if argc < 3:
        print(__USAGE__)
        sys.exit(1)
     
    in_dir = argv[1]
    MODELS_DIR = argv[2] 
    
    # Only train the model on the instruments passed in on the command line
    enabled_instruments = []
    idx = 3 
    while idx < argc:
        enabled_instruments.append(argv[idx])
        print(argv[idx])
        idx += 1

    datasets = glob.glob(in_dir + '/*.arff')
    print('Datasets:', datasets)
    for filename in datasets:
        train_model(filename, enabled_instruments)
    
