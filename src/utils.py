import csv
import logging

# declare the logging object
logger = logging.getLogger()


def get_content_type(extension):
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
    else:
        return None

    logger.info(f"content_type: {content_type}")
    return content_type


def make_json_from_csv(file, delimiter):
    logger.debug(f"make_json_from_csv('{file}', '{delimiter}') called")

    # open file and read in as csv
    with open(file) as f:
        csv_reader = csv.DictReader(f, delimiter=delimiter)
        # loop through each row and convert to json objects in an array
        json = [rows for rows in csv_reader]

    return json
