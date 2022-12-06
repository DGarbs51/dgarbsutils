import logging

import boto3
import botocore

# declare the logging object
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EventBridge:
    def __init__(self, profile=None, region="us-east-1"):
        self._region = region
        if profile:
            self._session = boto3.session.Session(profile_name=profile, region_name=self._region)
        else:
            self._session = boto3.session.Session(region_name=self._region)
        self._client = self._session.client("events")

    def enable_rule(self, rule_name, event_bus_name=None):
        """enables the specified rule"""
        try:
            if not event_bus_name:
                response = self._client.enable_rule(Name=rule_name)
            else:
                response = self._client.enable_rule(Name=rule_name, EventBusName=event_bus_name)
            logger.info(f"response: {response}")
            return response
        except botocore.exceptions.ClientError as error:
            logger.error(f"error: {error}")
            return None

    def disable_rule(self, rule_name, event_bus_name=None):
        """enables the specified rule"""
        try:
            if not event_bus_name:
                response = self._client.disable_rule(Name=rule_name)
            else:
                response = self._client.disable_rule(Name=rule_name, EventBusName=event_bus_name)
            logger.info(f"response: {response}")
            return response
        except botocore.exceptions.ClientError as error:
            logger.error(f"error: {error}")
            return None

    def list_rules(self, prefix=None, event_bus_name=None, next_token=None, limit=50):
        """lists the rules"""
        try:
            response = self._client.list_rules(
                NamePrefix=prefix, EventBusName=event_bus_name, NextToken=next_token, Limit=limit
            )
            logger.info(f"response: {response}")
            return response
        except botocore.exceptions.ClientError as error:
            logger.error(f"error: {error}")
            return None
