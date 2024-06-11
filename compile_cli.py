import glob

if __name__ == "__main__":
    possible_txt = glob.glob('*.txt')
    model_filename = ''
    for filename in possible_txt:
        if filename.endswith('ByteStr.txt'):
            model_filename = filename
            break
    
    model_file = open(model_filename, 'r')
    model_data = model_file.readline() 

    python_file = open('classinst.py', 'r')
    python_lines = python_file.readlines()
    
    python_lines[0] = model_data

    out_python = open('classinst.py', 'w')
    out_python.writelines(python_lines)

