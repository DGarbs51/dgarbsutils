import csv
import json
import logging
import random
import string
import sys

import psycopg2

from . import awsUtils

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_content_type(extension):
    """
    Returns the content type for a file extension.

        Parameters:
            extension (str): the file extension
        Returns:
            content_type (str): the content type for the file extension
    """
    logger.debug(f"get_content_type('{extension}') called")

    if extension == "xlsx":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif extension == "png":
        content_type = "image/png"
    elif extension == "jpg":
        content_type = "image/jpeg"
    elif extension == "jpeg":
        content_type = "image/jpeg"
    elif extension == "pdf":
        content_type = "application/pdf"
    elif extension == "eml":
        content_type = "binary/octet-stream"
    else:
        return None

    logger.info(f"content_type: {content_type}")
    return content_type


def make_csv_from_json(file, data, delimiter=None, keys=None):
    """
    Returns the full file path and delimiter for a csv file from a json string

        Parameters:
            file (str): The full path to the file to write to.
            data (str): The json string to convert to csv.
            delimiter (str, optional): The delimiter to use. Defaults to None.
            keys (list, optional): The keys to use in the csv file. Defaults to None.
        Returns:
            file (str): the full path to the file to write to
            delimiter (str): the delimiter the csv file used
    """
    logger.debug(f"make_csv_from_json('{file}','{data}','{delimiter}','{keys}') called")

    if not keys:
        keys = data[0].keys()
    if not delimiter:
        delimiter = "|"

    with open(file, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, delimiter=delimiter)
        w.writeheader()
        w.writerows(data)

    f.close()

    return file, delimiter


def make_json_from_csv(file, delimiter):
    """
    Returns a json string from a csv file

        Parameters:
            file (str): the full path to the file to read
            delimiter (str): the delimiter to use

        Returns:
            json (list): the json array of rows from the csv file
    """
    logger.debug(f"make_json_from_csv('{file}', '{delimiter}') called")

    if get_file_extension(file) not in ["txt", "csv", "ppe"]:
        message = f"file {file} is not a csv, txt, or ppe file"
        logger.error(message)
        raise Exception(message)

    csv.field_size_limit(sys.maxsize)
    # open file and read in as csv
    f = open(file, "r")
    csv_reader = csv.DictReader(f, delimiter=delimiter)
    # loop through each row and convert to json objects in an array
    output = list(csv_reader)

    return output


def get_file_extension(file):
    """
    Returns the file extension from a file name

        Parameters:
            file (str): the full path to the file to extract the extension from

        Returns:
            extension (str): the file extension
    """
    logger.debug(f"get_file_extension('{file}') called")

    extension = file.split(".")[-1]

    return extension


def randStr(chars=string.ascii_letters + string.digits, N=2):
    """
    Returns a random string of length N generated from the chars parameter

        Parameters:
            chars (list, optional): List of charachters to use for generation. Defaults to string.ascii_letters+string.digits.
            N (int, optional): Length of string generated. Defaults to 2.

        Returns:
            (str): Random string of length N using chars
    """
    return "".join(random.choice(chars) for _ in range(N))


class Postgres:
    def __init__(self, secrets_manager_key=None, host=None, port=None, user=None, password=None, dbname=None):
        self.secrets_manager_key = secrets_manager_key
        if self.secrets_manager_key:
            secret = json.loads(awsUtils.secrets_manager_get_secret(self.secrets_manager_key))
            host = secret["host"]
            port = secret["port"]
            dbname = secret["dbname"]
            user = secret["username"]
            password = secret["password"]

        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def execute_pgsql_query(self, sql):
        """executes a psql query"""
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except psycopg2.Error as e:
            return str(e)
        else:
            self.conn.commit()
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return results
        finally:
            cur.close()

        return None

    def close(self):
        self.conn.close()
