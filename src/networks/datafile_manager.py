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
    data = {k: float(v) for k, v in data}

    return data


if __name__ == "__main__":
    print("Loading data... ")
    d = load_data("training_data.txt")

    print(f"There are currently {len(d)} training samples.")

    output_keys = tuple(d.keys())[:1280000]
    output_dict = {k: d[k] for k in output_keys}
    print(f"Now there are {len(output_dict)} training samples.")

    print("Saving data... ")
    save_data(output_dict, "training_data_clipped.txt")
