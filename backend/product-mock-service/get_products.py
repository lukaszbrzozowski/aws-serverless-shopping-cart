import json
import os

from aws_lambda_powertools import Logger, Tracer
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

logger = Logger()
tracer = Tracer()

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("aws-serverless-productdatabase")


HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}

def change_list_from_decimal(l):
    for i, e in enumerate(l):
        if isinstance(e, Decimal):
            l[i] = change_num_from_decimal(e)
        if isinstance(e, dict):
            l[i] = change_dict_from_decimal(e)
        if isinstance(e, list):
            l[i] = change_list_from_decimal(e)
    return l

def change_num_from_decimal(val):
    if val % 1 == 0:
        val = int(val)
    else:
        val = float(val)
    return val

def change_dict_from_decimal(dictionary):
    for k in dictionary.keys():
        e = dictionary[k]
        if isinstance(e, Decimal):
            dictionary[k] = change_num_from_decimal(e)
        if isinstance(e, dict):
            dictionary[k] = change_dict_from_decimal(e)
        if isinstance(e, list):
            dictionary[k] = change_list_from_decimal(e)
    return dictionary


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    Return list of all products.
    """
    logger.debug("Fetching product list")

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"products": [change_dict_from_decimal(e) for e in table.scan()["Items"]]}),
    }
