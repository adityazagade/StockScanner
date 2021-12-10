import os
import logging
import json
import os.path

logger = logging.getLogger(__name__)


def save_to_csv(file_name, content, overwrite=False):
    directory_name = "downloads"
    logger.info(os.getcwd())
    directory_path = os.path.join(os.getcwd(), directory_name)
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    path = os.path.join(directory_path, file_name)
    with open(path, 'wb') as f:
        f.write(content)
    logger.info(f"file {file_name} successfully saved")


def append_to_file(fname, content):
    file1 = open(fname, "a")
    # writing newline character
    file1.write(content)
    file1.close()


def file_exists(fname):
    return os.path.isfile(fname)


def read_json_file(file_name):
    logger.info(os.getcwd())
    # Opening JSON file
    f = open(file_name)
    # returns JSON object as a dictionary
    data = json.load(f)
    f.close()
    return data
