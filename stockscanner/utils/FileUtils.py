import os
import logging
import json

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


def file_exists(file_name):
    return True


def read_json_file(file_name):
    logger.info(os.getcwd())
    # Opening JSON file
    f = open(file_name)
    # returns JSON object as a dictionary
    data = json.load(f)
    f.close()
    return data
