'''
**************************************************************************************************
* Filename:    extractFreqARFF.py                                                                *
*                                                                                                *
* Description: Runs an fft algorithm on all wav files in a folder and produces an arff files with*
*              the supplied number of top harmonics.                                             *
*                                                                                                *
*              This is a slightly modified version of a script created by Dr. Parson of Kutztown *
*              University. This file was originally used as part of an assignment for CSC458     *
*              - Data mining and Analytics I. All credit for the guts of this file goes to him   *
*              the original can be found here:                                                   *
*              https://faculty.kutztown.edu/parson/spring2024/CSC458Spring2024Assn1.html         *
*                                                                                                *
* Usage:       python3 extractFreqARFF.py <numharmonics> <audiodir> <outfilename>                *
*                   <numharmonics> - The number of top amplitude harmonics to include            *
*                   <audiodir>     - The folder containing the audio files to process            *
*                   <outfilename>  - The name of the final arff file. No extension should        *
*                                    be provided                                                 *
*                                                                                                *
**************************************************************************************************
'''
from scipy.io import wavfile
from scipy.fft import fft 
import numpy as np
import csv
import sys
import os
import glob

import tqdm

# NFFTharmonics = 128          # How many strongest bins to use without sort.
# # DEBUG LEN OF unsortedFFT: 22050 NFFTharmonics for sampling rate 44100
# NRndTrainLimit = 5          # How many of each in NRndTrain.arff, tid != 0
# NRndTrainCount = {
#     'SinOsc' : 0 ,
#     'TriOsc' : 0 ,
#     'SqrOsc' : 0 ,
#     'SawOsc' : 0 ,
#     'PulseOsc' : 0
# }
SeenInstruments = set() 

def wav2arff(fpath, openarffcsv, rawarffcsv, number_harmonics):
    '''
    Normalize the first Nharmonics of the WAV file in parameter *fpath*
    as ratios of amplitude relative to the first harmonic of amplitude 1.0,
    and the frequency of the harmonic as a multiple of the fundamental 1.0,
    and makes the Nharmonics into Weka attributes for classification of the
    waveform type. Note that non-harmonic signals above the fundamental with
    adequate amplitude may be in noisy data. This function writes one row
    of data to the open CSV file *openarffcsv* via writeRow().
    Base string for fpath must embed type tag as the second underline-separated
    field like this:
        lazy1_SqrOsc_993_0.574001525357_0.189810423535_659894.wav
    10/23/2021 N.P. add fftfilecsv, fftnoiselesscsv, fftnoiseycsv,
        fftrndarffcsv files for unsorted FFT.
    Return value is None.
    '''

    filename = os.path.split(fpath) 
    instrument = filename[1].split('_')
    toosc = instrument[0]
    SeenInstruments.add(toosc)

    samplerate, data = wavfile.read(fpath)
    normdata = list(data)
    complexfft = fft(normdata)
    absfft = np.abs(complexfft) # type:ignore
    
    # 6/4/2021, 6/6/2021 FFT ANALYSIS:
    # discard mirror image right of center, sort on amplitude.
    freqstep = 1    # needed to find fundamental frequency and the harmonics
    sortedfft = []
    unsortedFFT = []            # N.P.
    # sort is pulling in low-frequency pulse noise below 100 Hz,
    # or possibly low-freq white noise for sine waves, so cut those out:
    nyquist = samplerate / 2.0      # 3/1/2023
    perbin = nyquist / int(len(absfft)/2) # 3/1/2023
    numbinsBelow100 = int(100 / perbin) # 3/1/2023
    # print("DEBUG numbinsBelow100 ", numbinsBelow100)
    for ix in range(0, int(len(absfft)/2)):
        if ix >= numbinsBelow100:   # 3/1/2023
            sortedfft.append([absfft[ix], freqstep]) 
        unsortedFFT.append(absfft[ix])          # N.P.
        freqstep += 1
    sortedfft.sort(reverse=True, key=lambda inst : inst[0])
    # ^^^^^ sort on frequencyAmplitude
    fundamentalAmplitude = sortedfft[0][0] * 1.0
    fundamentalFrequency = sortedfft[0][1] * 1.0
    wekaDataRow = []
    rawDataRow = []
    for inst in sortedfft[0:number_harmonics]:
        # round to nearest multiple of the fundamental
        # Because of aliasing we need to keep some fractional digits.
        wekaDataRow.extend([round(inst[0]/fundamentalAmplitude, 6),
            round(inst[1]/fundamentalFrequency, 6)])
        rawDataRow.extend([round(inst[0], 6), round(inst[1], 6)])

    wekaDataRow.extend([toosc])
    rawDataRow.extend([toosc])

    openarffcsv.writerow(wekaDataRow)
    rawarffcsv.writerow(rawDataRow)

    return None

# Allows me to import it
# TODO: FIX REPEAT LATER, this is just a hacky solution for now
def create_arff(audiofolder, number_harmonics, outarff_filename_starter, outdir):
    WavPathsList = glob.glob(audiofolder + '*.wav')

    openarfffile = open(outdir + outarff_filename_starter + 'Normalized.arff', 'w',
        newline='')
    rawarffile = open(outdir + outarff_filename_starter + 'Raw.arff', 'w')
    
    for of in [openarfffile, rawarffile]:
        of.write("@relation " + outarff_filename_starter + "\n")
        for i in range(1, number_harmonics+1):
            of.write("@attribute ampl" + str(i) + " numeric\n")
            of.write("@attribute freq" + str(i) + " numeric\n")
        of.write("@attribute instrument\n")
        of.write("@data\n")
        of.flush()

    openarffcsv = csv.writer(openarfffile, delimiter=',', quotechar='"')
    rawarffcsv = csv.writer(rawarffile, delimiter=',', quotechar='"')

    pbar = tqdm.tqdm(desc='Analyzing audio', total=len(WavPathsList))
    for idx, path in enumerate(WavPathsList):
        # print('Analyzing audio', str(idx) + '/' + str(totalfiles))
        wav2arff(path, openarffcsv, rawarffcsv, number_harmonics) # N.P. add
        pbar.update(1)

    openarfffile.close()
    rawarffile.close()

    openarfffile = open(outdir + outarff_filename_starter +'Normalized.arff', 'r')
    rawarffile = open(outdir + outarff_filename_starter +'Raw.arff', 'r')
    
    for file in [openarfffile, rawarffile]:
        data = file.readlines()

        for idx, line in enumerate(data):
            if line == "@attribute instrument\n":
                newline = '@attribute instrument {'
                numinst = len(SeenInstruments)
                for idy, inst in enumerate(SeenInstruments):
                    if idy == (numinst - 1):
                        newline += inst + '}\n'
                    else:
                        newline += inst + ','
                data[idx] = newline
                break 

        file.close()            
        outfile = open(file.name, 'w')
        outfile.writelines(data)
        outfile.close()

__USAGE__ =                                                         \
'python3 extractFreqARFF.py <Number of Harmonics> <audio dir> <outputfilename (no ext)>'
# 'python extractAudioFreqARFF.py moduleWithWavPaths outARFFname [ Nharmonics ]'

if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)

    if argc != 4 and argc < 5:
        print("USAGE", __USAGE__)

    # Case in which the user wants to create the entire arff file
    if argc == 4:
        if int(argv[1]) < 8:
            sys.stderr.write("ERROR, Nharmonics must be at least 8: " + sys.argv[1] + '\n')
            sys.exit(1)
            
        WavPathsList = glob.glob(argv[2] + '*.wav')
        number_harmonics = int(argv[1])

        openarfffile = open(argv[3] + 'Normalized.arff', 'w',
            newline='')
        rawarffile = open(argv[3] + 'Raw.arff', 'w')
        
        for of in [openarfffile, rawarffile]:
            of.write("@relation " + argv[3] + "\n")
            for i in range(1, number_harmonics+1):
                of.write("@attribute ampl" + str(i) + " numeric\n")
                of.write("@attribute freq" + str(i) + " numeric\n")
            of.write("@attribute instrument\n")
            of.write("@data\n")
            of.flush()
        openarffcsv = csv.writer(openarfffile, delimiter=',', quotechar='"')
        rawarffcsv = csv.writer(rawarffile, delimiter=',', quotechar='"')

        totalfiles = len(WavPathsList)

        pbar = tqdm.tqdm(desc='Analyzing audio', total=len(WavPathsList))
        for idx, path in enumerate(WavPathsList):
            # print('Analyzing audio', str(idx) + '/' + str(totalfiles))
            wav2arff(path, openarffcsv, rawarffcsv, number_harmonics) # N.P. add
            pbar.update(1)

        openarfffile.close()
        rawarffile.close()

        openarfffile = open(argv[3]+'Normalized.arff', 'r')
        rawarffile = open(argv[3]+'Raw.arff', 'r')
        
        for file in [openarfffile, rawarffile]:
            data = file.readlines()

            for idx, line in enumerate(data):
                if line == "@attribute instrument\n":
                    newline = '@attribute instrument {'
                    numinst = len(SeenInstruments)
                    for idy, inst in enumerate(SeenInstruments):
                        if idy == (numinst - 1):
                            newline += inst + '}\n'
                        else:
                            newline += inst + ','
                    data[idx] = newline
                    break 

            file.close()            
            outfile = open(file.name, 'w')
            outfile.writelines(data)
            outfile.close()

        
        # openarfffile = open(argv[3], 'w')
        # openarfffile.writelines(data)
        # openarfffile.close()
    # The case in which this porgram is being called to create a small subset of files so that they can later be combined
    elif argc >= 5:
        pass
