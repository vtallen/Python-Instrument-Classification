import glob

if __name__ == "__main__":
    possible_txt = glob.glob('/*.txt')

    model_txt = possible_txt[0]

    model_file = open(model_txt, 'r')
    model_data = model_file.readlines()

    python_file = open('cli_tool.py', 'r')
    python_lines = python_file.readlines()
    
    python_lines[0] = model_data[0]

