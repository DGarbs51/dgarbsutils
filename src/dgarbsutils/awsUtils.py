import os
import boto3
import logging
import botocore
import tempfile
from . import utils

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def dynamodb_generate_json_from_csv_in_s3(bucket, key, delimiter=","):
    """takes a bucket and key and returns a dynamodb json formatted payload"""
    logger.debug(f"")

    file = s3_download(bucket, key)
    logger.info(f"file: {file}")
    data = utils.make_json_from_csv(file, delimiter)
    logger.debug(f"data: {data}")

    output = []
    for row in data:
        item = dynamodb_format_json(row)
        output.append(item)
        logger.debug(f"item: {item}")

    os.remove(file)
    return output

def dynamodb_translate_data_type(data):
    data_type = str(type(data))

    if data_type == "<class 'str'>":
        if " ".join(data.split()) == "":
            return "NULL"
        return "S"
    if data_type in ["<class 'int'>", "<class 'float'>", "<class 'complex'>"]:
        return "N"
    if data_type == "<class 'list'>":
        return "L"
    if data_type == "<class 'dict'>":
        return "M"
    if data_type == "<class 'bool'>":
        return "BOOL"
    if data_type == "<class 'NoneType'>":
        return "NULL"


def dynamodb_format_json(data):
    """formats the dynamodb json"""
    logger.debug(f"dynamodb_format_json('{data}') called")

    output = {}
    keys = list(data.keys())
    for key in keys:
        output[key] = {dynamodb_translate_data_type(data[key]): data[key]}
    return output

def dynamodb_add_nested_json(pk_name, pk_value, data):
    """generates the nested data to add to a dynamodb item"""
    output = []
    for row in data:
        if row[pk_name]["S"] == pk_value:
            output.append({"M": row})

    return output


def sqs_delete_message(receipt_handle):
    """deletes a message from the SQS queue"""
    logger.debug(f"sqs_delete_message('{receipt_handle}') called")

    s = boto3.session.Session()
    c = s.client(
        service_name="sqs",
        region_name=os.environ["AWS_REGION"],
    )

    # delete the message that has been processed
    try:
        c.delete_message(QueueUrl=os.environ["SQS_QUEUE_URL"], ReceiptHandle=receipt_handle)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            logger.error(f"The queue {os.environ['SQS_QUEUE_URL']} does not exist")
        else:
            raise e
    else:
        logger.info(f"sqs message {receipt_handle} deleted")


def sqs_send_message(body):
    """sends a message to the SQS queue"""
    logger.debug('send_sqs_message("body") called')

    # establich a boto3 client for SQS
    s = boto3.session.Session()
    c = s.client("sqs")
    logger.info("boto3 sqs client created")

    try:
        # send the message to the SQS Queue
        c.send_message(QueueUrl=os.environ["SQS_QUEUE_URL"], MessageBody=body)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            logger.error(f"The queue {os.environ['SQS_QUEUE_URL']} does not exist")
        else:
            raise e
    else:
        logger.info("sqs message sent")


def secrets_manager_get_secret(secret):
    """gets the secret from the secrets manager"""
    logger.debug(f'secrets_manager_get_secret("{secret}") called')

    secret_name = secret

    s = boto3.session.Session()
    c = s.client(
        service_name="secretsmanager",
        region_name=os.environ["AWS_REGION"],
    )
    logger.info("boto3 secretsmanager client created")

    try:
        get_secret_value_response = c.get_secret_value(SecretId=secret_name)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error(f"The requested secret {secret_name} was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logger.error(f"The request was invalid due to: {e}")
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logger.error(f"The request had invalid params: {e}")
        elif e.response["Error"]["Code"] == "DecryptionFailure":
            logger.error(f"The requested secret can't be decrypted using the provided KMS key: {e}")
        elif e.response["Error"]["Code"] == "InternalServiceError":
            logger.error(f"An error occurred on service side: {e}")
        else:
            raise e
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary
        # only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            text_secret_data = get_secret_value_response["SecretString"]
            return text_secret_data
        binary_secret_data = get_secret_value_response["SecretBinary"]
        return binary_secret_data

    return None


def s3_download(bucket, key):
    """downloads a file from s3"""
    logger.debug(f's3_download("{bucket}", "{key}") called')

    s = boto3.session.Session()
    c = s.resource("s3")
    logger.info("boto3 s3 client created")

    temp_file = tempfile.NamedTemporaryFile(suffix=f".{utils.get_file_extension(key)}", delete=False)
    local_path = temp_file.name

    try:
        c.Bucket(bucket).download_file(key, local_path)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error(f"The object {key} does not exist")
        else:
            raise e
    else:
        logger.info(f"{key} downloaded to {local_path}")
        return local_path

    return None


def s3_upload(bucket, key, local_path):
    """uploads a file to s3"""
    logger.debug(f's3_upload("{bucket}", "{key}", "{local_path}") called')

    s = boto3.session.Session()
    c = s.resource("s3")
    logger.info("boto3 s3 client created")

    try:
        c.Bucket(bucket).upload_file(local_path, key)
    except botocore.exceptions.ClientError as e:
        logger.exception("error while loading the file to s3")
        raise e
    else:
        logger.info(f"{local_path} uploaded to {bucket}/{key}")
