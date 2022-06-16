import csv
import logging

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_content_type(extension):
    """gets the content type for a file extension"""
    logger.debug(f"get_content_type('{extension}') called")

    if extension == "xlsx":
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif extension == "png":
        content_type = "image/png"
    elif extension == "jpg":
        content_type = "image/jpeg"
    elif extension == "jpeg":
        content_type = "image/jpeg"
    elif extension == "pdf":
        content_type = "application/pdf"
    else:
        return None

    logger.info(f"content_type: {content_type}")
    return content_type


def make_json_from_csv(file, delimiter):
    """makes a json list from a csv file"""
    logger.debug(f"make_json_from_csv('{file}', '{delimiter}') called")

    if get_file_extension(file) not in ["txt", "csv", "ppe"]:
        message = f"file {file} is not a csv, txt, or ppe file"
        logger.error(message)
        raise Exception(message)

    # open file and read in as csv
    f = open(file, "r")
    csv_reader = csv.DictReader(f, delimiter=delimiter)
    # loop through each row and convert to json objects in an array
    json = list(csv_reader)

    return json


def get_file_extension(file):
    """gets the file extension"""
    logger.debug(f"get_file_extension('{file}') called")

    extension = file.split(".")[-1]

    return extension
