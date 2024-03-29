'''
**************************************************************************************************
* Filename:    cleandata.py                                                                      *
*                                                                                                *
* Description: Opens the arff file generated by extractFreqARFF.py and removes all lines whose   *
*              first attribute is equal to 0.0 or nan. The files this data came from were either *
*              silence or did not have enough audio information to perform an FFT. Lines whose   *
*              length is less than the number of header attributes are also discarded. This can  *
*              happen when there are not enough peaks in the fft to produce a full 32            *
*                                                                                                *
* Usage:       python3 cleandata.py <infile> <outffile>                                          *
*                   <infile>    - The file to clean                                              *
*                   <outfile>   - The destination filename, can be the same as <infile>          *
*                                 it does not exist                                              *
*                                                                                                *
*              python3 cleandata.py <folder> - Cleans all files in a given folder.               *
*                                              Does so inplace                                   *
*                   <folder>    - The folder to clean arff files from                            *
**************************************************************************************************
'''
import csv
import sys
import glob
import os

__USAGE__ = "USAGE:"\
        "python3 cleandata.py <infile.arff> <outfile.arff> - cleans a single file"\
        "python3 cleandata.py <filesdir> - cleans all arff files in <filesdir>"

'''
* ********************************************************************************************** *
*                                                                                                *
* Name:             clean_file                                                                   *
*                                                                                                *
* Parameters:       str filename         - The file to clean                                     *
*                   str outfilename = '' - The file to save the cleaned file as. Defaults to     *
*                                          the value of filename (clean in place)                *
*                                                                                                *
* Purpose:          Removes bad data from the given arff file. These are lines that contain no   *
*                   audio data, so they start with a 0 or nan. Also removes short rows. These    *
*                   occur when there is not enough audio data in a snippet to extract all the    *
*                   requested harmonics                                                          *
*                                                                                                *
* ********************************************************************************************** *
'''
def clean_file(filename, outfilename):
    file = open(filename, 'r')
    header = []
    numcols = 0

    line = file.readline().strip()
    while True:
        header.append(line)
        if line.startswith('@attribute'):
            numcols += 1

        if line == '@data':
            break


        line = file.readline().strip()
    
    incsv = csv.reader(file)
    data = []
    for row in incsv:
        data.append(row) 

    file.close()

    # inCSV = csv.reader(file)
    outfile = open(outfilename, 'w')
    for line in header:
        outfile.write(line + '\n')

    outcsv = csv.writer(outfile)
    
    # excludes rows that have 0.0 ampl vals, nan, or all attributes are not filled 
    for row in data:
        if len(row) != numcols:
            print('Short row:', row)
        if row[0] != 'nan' and row[0] != '0.0' and len(row) == numcols:
            outcsv.writerow(row)

    outfile.close()


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc != 3 and argc != 2:
        print(__USAGE__)
        sys.exit(1)
    
    if argc == 3:
        filename = argv[1]
        outfilename = argv[2]
        clean_file(filename, outfilename)
    elif argc == 2:
        files_to_clean = glob.glob(argv[1] + '*.arff')
        print('argv', argv)
        print('Cleaning files:', files_to_clean)
        for filename in files_to_clean:
            clean_file(filename, filename)
                  

