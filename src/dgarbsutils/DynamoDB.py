import logging
import os

import boto3
import botocore

from . import awsUtils, utils

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoDB:
    def __init__(self, table_name, profile=None, region="us-east-1"):
        self._region = region
        if profile:
            self._session = boto3.session.Session(profile_name=profile, region_name=self._region)
        else:
            self._session = boto3.session.Session(region_name=self._region)
        self._client = self._session.client("dynamodb")
        self._table_name = table_name

    def dynamodb_generate_json_from_csv_in_s3(self, bucket, key, delimiter=","):
        """takes a bucket and key and returns a dynamodb json formatted payload"""
        file = awsUtils.s3_download(bucket, key)
        logger.info(f"file: {file}")
        data = utils.make_json_from_csv(file, delimiter)
        logger.debug(f"data: {data}")

        output = []
        for row in data:
            item = self.dynamodb_format_json(row)
            output.append(item)
            logger.debug(f"item: {item}")

        os.remove(file)
        return output

    def dynamodb_translate_data_type(self, data):
        """translates the python data type to a dynamodb data type"""
        data_type = str(type(data))

        if data_type == "<class 'str'>":
            if " ".join(data.split()) == "":
                return {"NULL": True}
            return {"S": " ".join(data.split())}
        if data_type in ["<class 'int'>", "<class 'float'>", "<class 'complex'>"]:
            return {"N": data}
        if data_type == "<class 'list'>":
            return {"L": [self.dynamodb_translate_data_type(item) for item in data]}
        if data_type == "<class 'dict'>":
            return {"M": {key: self.dynamodb_translate_data_type(value) for key, value in data.items()}}
        if data_type == "<class 'bool'>":
            return {"BOOL": data}
        if data_type == "<class 'NoneType'>":
            return {"NULL": True}
        return None

    def dynamodb_convert_to_json(self, data):
        """converts the dynamodb json to a python json"""
        output = {}
        for key, inner in data.items():
            for data_type, value in inner.items():
                if data_type == "M":
                    output[key] = self.dynamodb_convert_to_json(value)
                elif data_type == "NULL":
                    output[key] = None
                elif data_type in ["L", "NS", "BS", "SS"]:
                    out = []
                    for items in value:
                        for _, list_value in items.items():
                            out.append(list_value)
                    output[key] = out
                else:
                    output[key] = value

        return output

    def dynamodb_put_item(self, data):
        """puts an item to dynamodb"""
        logger.debug(f'dynamodb_put_item( "{data}") called')

        try:
            self._client.put_item(TableName=self._table_name, Item=data)
        except botocore.exceptions.ClientError as e:
            logger.exception("error while putting the item to dynamodb")
            raise e
        else:
            logger.info(f"{data} put to {self._table_name}")

    def dynamodb_get_item(self, key_fields):
        """gets an item to dynamodb"""
        logger.debug(f'dynamodb_get_item( "{key_fields}") called')

        Key = self.dynamodb_format_json(key_fields)

        try:
            response = self._client.get_item(TableName=self._table_name, Key=Key)
        except botocore.exceptions.ClientError as e:
            logger.exception("error while getting the item from dynamodb")
            raise e
        else:
            logger.info(f"{response} from {self._table_name}")
            return response

    def dynamodb_format_json(self, data):
        """converts the python json to a dynamodb json"""
        logger.debug(f"dynamodb_format_json('{data}') called")

        output = {}
        keys = list(data.keys())
        for key in keys:
            output[key] = self.dynamodb_translate_data_type(data[key])
        return output

    @staticmethod
    def dynamodb_add_nested_json(pk_name, pk_value, data):
        """generates the nested data to add to a dynamodb item"""
        output = []
        for row in data:
            if row[pk_name]["S"] == pk_value:
                output.append({"M": row})

        return output

    def dynamodb_update_item(self, key_fields, update_fields, start_key=None):

        Key = self.dynamodb_format_json(key_fields)
        Names = {}
        if start_key:
            rand_start = utils.randStr()
            Names[f"#{rand_start}"] = start_key
        Values = {}
        Expression = "SET "
        for update_field in update_fields:
            random_str = utils.randStr()
            x = self.dynamodb_format_json(update_field)
            for y, z in x.items():
                Names[f"#{random_str}"] = y
                Values[f":{random_str}"] = z
                if not start_key:
                    Expression += f"#{random_str} = :{random_str}, "
                else:
                    Expression += f"#{rand_start}.#{random_str} = :{random_str}, "

        Expression = Expression.rstrip(", ")

        response = self._client.update_item(
            ExpressionAttributeNames=Names,
            ExpressionAttributeValues=Values,
            Key=Key,
            ReturnValues="UPDATED_NEW",
            TableName=self._table_name,
            UpdateExpression=Expression,
        )

        return response
