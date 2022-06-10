import os
import uuid
import boto3
import logging
import botocore
from pathlib import Path
from urllib.parse import unquote_plus

# declare the logging object
logger = logging.getLogger()

# get working directory to reference relative files
path = Path(__file__).parent
logger.debug(f"path: {path}")


def sqs_delete_message(receipt_handle):
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
    logger.info(f'send_sqs_message("body") called')

    # establich a boto3 client for SQS
    s = boto3.session.Session()
    c = s.client("sqs")
    logger.info(f"boto3 sqs client created")

    try:
        # send the message to the SQS Queue
        c.send_message(QueueUrl=os.environ["SQS_QUEUE_URL"], MessageBody=body)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
            logger.error(f"The queue {os.environ['SQS_QUEUE_URL']} does not exist")
        else:
            raise e
    else:
        logger.info(f"sqs message sent")


def secrets_manager_get_secret(secret):
    secret_name = secret

    s = boto3.session.Session()
    c = s.client(
        service_name="secretsmanager",
        region_name=os.environ["AWS_REGION"],
    )
    logging.info(f"boto3 secretsmanager client created")

    try:
        get_secret_value_response = c.get_secret_value(SecretId=secret_name)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error(f"The requested secret {secret_name} was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logger.error("The request was invalid due to:", e)
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logger.error("The request had invalid params:", e)
        elif e.response["Error"]["Code"] == "DecryptionFailure":
            logger.error("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response["Error"]["Code"] == "InternalServiceError":
            logger.error("An error occurred on service side:", e)
        else:
            raise e
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            text_secret_data = get_secret_value_response["SecretString"]
            return text_secret_data
        else:
            binary_secret_data = get_secret_value_response["SecretBinary"]
            return binary_secret_data


def s3_download(bucket, key):
    logger.info(f's3_download("{bucket}", "{key}") called')

    s = boto3.session.Session()
    c = s.resource("s3")
    logger.info(f"boto3 s3 client created")

    tmpkey = unquote_plus(key).replace("/", "")
    local_path = f"/tmp/{uuid.uuid4()}{tmpkey}"

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
