"""
File: datafile_manager.py

Description: Helper module for interaction with the testing and training data files.
"""


def save_data(data, filename):
    data = "\n".join(f"{k}:{v}" for k, v in data.items()) + "\n"

    save_file = open(filename, "w")
    save_file.write(data)
    save_file.close()


def load_data(filename):
    save_file = open(filename, "r")
    data = save_file.readlines()
    save_file.close()

    data = (entry[:-1].split(":") for entry in data)
    data = {k: 2 * float(v) - 1 for k, v in data}

    return data


if __name__ == "__main__":
    LOAD_FILE = "training_data.txt"
    SAVE_FILE = "training_data_clipped.txt"
    OUTPUT_SIZE = 1280000

    print(f"Loading data from {LOAD_FILE}... ")
    d = load_data(LOAD_FILE)

    print(f"There are currently {len(d)} training samples.")

    output_keys = tuple(d.keys())[:OUTPUT_SIZE]
    output_dict = {k: d[k] for k in output_keys}
    print(f"Choosing first {len(output_dict)} training samples.")

    print(f"Saving new data in {SAVE_FILE}... ")
    save_data(output_dict, SAVE_FILE)
