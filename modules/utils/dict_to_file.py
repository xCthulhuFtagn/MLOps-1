import json
from filelock import FileLock
import os

def write_dict_to_file(file_path, data):
    """
    Write a dictionary to a JSON file.

    Args:
        file_path (str): The path to the file where the dictionary will be written.
        data (dict): The dictionary to be written to the file.

    Returns:
        None
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w+') as file:
            json.dump({},file)

    lock = FileLock(file_path + '.lock')
    with lock:
        with open(file_path, 'w') as file:
            json.dump(data, file)

def read_dict_from_file(file_path):
    """
    Read a dictionary from a JSON file.

    Args:
        file_path (str): The path to the file from which the dictionary will be read.

    Returns:
        dict: The dictionary read from the file.
    """

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w+') as file:
            json.dump({},file)
    
    lock = FileLock(file_path + '.lock')
    with lock:
        with open(file_path, 'r+') as file:
            data = json.load(file)

    return data