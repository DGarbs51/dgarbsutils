import logging
import time
from datetime import datetime

import boto3

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Cloudwatch:
    def __init__(self, log_group, profile=None, region="us-east-1"):

        self._region = region
        if profile:
            self._session = boto3.session.Session(profile_name=profile, region_name=self._region)
        else:
            self._session = boto3.session.Session(region_name=self._region)
        self._client = self._session.client("logs")
        self._log_group = log_group

    def start_query(self, query, start_time=None, end_time=None):
        """Query CloudWatch Logs and return the results as a JSON string."""

        if start_time is None:
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_time = datetime.strptime(start_time, "%Y-%m-%d")

        if end_time is None:
            end_time = datetime.now()
        else:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")

        start_query_response = self._client.start_query(
            logGroupName=self._log_group,
            startTime=int(start_time.timestamp()),
            endTime=int(end_time.timestamp()),
            queryString=query,
        )

        query_id = start_query_response["queryId"]
        logger.info(query_id)

        response = None

        while response == None or response["status"] == "Running":
            logger.info("Waiting for query to complete ...")
            time.sleep(1)
            return query_id

    def get_query_results(self, query_id):
        response = self._client.get_query_results(queryId=query_id)
        return response

    def convert_results_to_json(self, response):
        items = []
        for result in response["results"]:
            item = {}
            for field in result:
                if field["field"] != "@ptr":
                    item[field["field"]] = field["value"]
                items.append(item)

        return items

    def query_to_json(self, query, start_time=None, end_time=None):
        query_id = self.start_query(query, start_time, end_time)
        response = self.get_query_results(query_id)
        return self.convert_results_to_json(response)
