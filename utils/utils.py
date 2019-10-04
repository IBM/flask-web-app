# -*- coding: utf-8 -*-
"""
Common method for reuse code

Generate certificate

openssl req -x509 -out localhost.crt -keyout localhost.key \
  -newkey rsa:2048 -nodes -sha256 \
  -subj '/CN=localhost' -extensions EXT -config <( \
   printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")


"""
import json
import logging
import os
import random
import shutil
import string
import zipfile
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger()

levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


def init_main_data(config_file):
    """
    Parse the configuration file and return the necessary data for initalize the tool
    :param config_file:
    :return:
    """

    if not os.path.exists(config_file):
        print("File {} not found!".format(config_file))
        return None, None
    if not os.path.isfile(config_file):
        print("File {} is not a file!".format(config_file))
        return None, None

    with open(config_file) as f:
        CFG = json.load(f)

    if not os.path.exists(CFG["logging"]["path"]):
        os.makedirs(CFG["logging"]["path"])

    logger = load_logger(CFG["logging"]["level"], CFG["logging"]["path"], CFG["logging"]["prefix"])

    return CFG, logger


def load_logger(level, path, name):
    logger = logging.getLogger()  # set up root logger
    filename = os.path.join(path, name)
    handler = TimedRotatingFileHandler(filename, when='H')
    handler.suffix = "%Y-%m-%d.log"
    handler.extMatch = r"^\d{4}-\d{2}-\d{2}\.log$"

    level = levels[level]
    handler.setLevel(level)  # set level for handler
    formatter = '%(asctime)s - %(name)s - %(levelname)s | [%(filename)s:%(lineno)d] | %(message)s'
    handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def random_string(string_length=10):
    """
    Generate a random string of fixed length
    :param string_length:
    :return:
    """
    letters = string.ascii_lowercase
    data = ""
    for character in range(string_length):
        data += random.choice(letters)
    return data


def zip_data(file_to_zip, path):
    log.debug("zip_data | Zipping file " + file_to_zip)
    shutil.make_archive(file_to_zip, 'zip', path)


def unzip_data(unzipped_folder, zip_file):
    """
    Unzip the zip file in input in the given 'unzipped_folder'
    :param unzipped_folder:
    :param zip_file:
    :return: The name of the folder in which find the unzipped data
    """
    folder_name = os.path.join(unzipped_folder, random_string())
    log.debug("unzip_data | Unzipping {} into {}".format(zip_file, folder_name))
    zip_ref = zipfile.ZipFile(zip_file)
    zip_ref.extractall(folder_name)
    zip_ref.close()
    log.debug("unzip_data | File uncompressed!")
    return folder_name


def remove_dir(directory):
    """
    Wrapper for remove a directory
    :param directory:
    :return:
    """
    log.debug("remove_dir | Removing directory {}".format(directory))
    if os.path.isdir(directory):
        shutil.rmtree(directory)


def secure_request(request):
    #request.headers['Content-Security-Policy'] = "default-src 'self'"
    request.headers['Feature-Policy'] = "geolocation 'none'; microphone 'none'; camera 'none'"
    request.headers['Referrer-Policy'] = 'no-referrer'
    request.headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
    request.headers['X-Content-Type-Options'] = 'nosniff'
    request.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    request.headers['X-XSS-Protection'] = '1; mode=block'

    return request
