from __future__ import print_function

import os
import json
import boto3
from botocore.vendored import requests
from botocore.exceptions import ClientError
import random
import logging
# from elasticsearch import Elasticsearch, RequestsHttpConnection, urllib
# from requests_aws4auth import AWS4Auth
# from aws_requests_auth.aws_auth import AWSRequestsAuth


ES_HOST = 'https://search-chatbot-najlxvv2ws7iy4mnqwtniy2ori.us-east-1.es.amazonaws.com'
# ES_INDEX = 'predictions'
# ES_TYPE = 'Prediction'
ACCESS_KEY = 'AKIAQ62D5RI7LQWPAH42'
SECRET_ACCESS_KEY = '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'
REGION = 'us-east-1'
# URL = ES_HOST + '/' + ES_INDEX + '/' + ES_TYPE + '/_search'
SQS_URL = 'https://sqs.us-east-1.amazonaws.com/066177567294/requests'
SENDER = 'zt586@nyu.edu'

### --- Establish connection to ES --- ### 

# credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

###  --- Get random restaurant recommendations --- ### 

logger = logging.getLogger()

def search_dynamodb(restaurants, req):
    dynamodb = boto3.client('dynamodb')
    
    cuisine = req["cuisine"].lower()
    rest_dic, name_list = {}, []

    for item in restaurants:
        rest_id = item["_source"]["id"]
        rest_name = item["_source"]["name"]
        
        response = dynamodb.get_item(
            TableName='yelp-restaurants',
            Key={
                'cuisine': {
                    'S': cuisine
                },
                'id': {
                    'S': rest_id
                }
            }
        )
        # print("RESPONSE: {}".format(json.dumps(response)))

        address = response["Item"]["location"]["M"]["address1"]["S"]
        if rest_name not in rest_dic:
            rest_dic[rest_name] = address
        
    
    number_people = req["number_people"]
    dining_date = req["dining_date"]
    dining_time = req["dining_time"]
    location = req["location"]

    for name in rest_dic:
        name_list.append(name)
    
    print("REST_DICT --- {}".format(rest_dic))
    print("NAME_LIST --- {}".format(name_list))
    
    reservation = 'Hello! Here are my {} restaurant suggestions for {} people, on {}, {} at {}: (1). {} located at {} (2). {} located at {} (3). {} located at {}. Enjoy your meal!'.format(cuisine, number_people, dining_date, dining_time, location, name_list[0], rest_dic[name_list[0]], name_list[1], rest_dic[name_list[1]], name_list[2], rest_dic[name_list[2]])

    return reservation

def get_url(es_index, es_type, cuisine):
    url = ES_HOST + '/' + es_index + '/' + es_type + '/_search'
    search_url = url + '?q=' + cuisine
    return search_url

def lambda_handler(event, context):

    headers = { "Content-Type": "application/json" }

    sqs = boto3.client('sqs')
    receipt_handle = event["Records"][0]["receiptHandle"]

    # pulls a message from the SQS
    for record in event["Records"]:
        req = json.loads(record["body"])
        """
        {
            "location": "NY",
            "cuisine": "Chinese",
            "number_people": "2",
            "dining_date": "2019-04-18",
            "dining_time": "18:00"
            "email": xxx                
        }
        """
    print("REQ -- {}".format(json.dumps(req)))
    
    # make the HTTP request
    cuisine = req["cuisine"].lower()
    url = get_url('predictions', 'Prediction', cuisine)
    r = requests.get(url, headers=headers)
    r_data = r.json()
    all_restaurants = r_data["hits"]["hits"] # list type

    # get Machine Learning recommendation from ElasticSearch
    if len(all_restaurants) < 3:
        rest_url = get_url('restaurants', 'Restaurant', cuisine)
        r = requests.get(rest_url, headers=headers)
        r_data = r.json()
        all_restaurants = r_data["hits"]["hits"] # list type

        # get randome restaurant recommendation from ElasticSearch
        restaurants = random.sample(all_restaurants, 3) # list type, [{}, {}, {}]
        # fetch more information form DynamoDB
        reservation = search_dynamodb(restaurants, req)

    else:
        restaurants = random.sample(all_restaurants, 3) # list type, [{}, {}, {}]
        reservation = search_dynamodb(restaurants, req)

    
### --- send text confirmation by SNS --- ###
    email = str(req["email"])

    # send SES message
    ses = boto3.client('ses', region_name=REGION)

    print("EMAIL ADDRESS: {}".format(email))

    message = ses.send_email(
        Source=SENDER,
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Body': {
                'Text': {
                    'Data': reservation
                }
            },
            'Subject': {
                'Data': 'Restaurant Suggestions from Chatbot'
            }
        }
    )
        
    print("TEST EMAIL IF SENT") 
    print("--- MESSAGE --- {}".format(message))

    # message = ses.send_email(
    #     Source=email,
    #     Message=reservation
    # )

    # delete the finished request from SQS  
    sqs.delete_message(
        QueueUrl=SQS_URL,
        ReceiptHandle=receipt_handle
    )
    print("SUCCESSFULLY DETELE THE FINISHED MESSAGE FROM SQS")

    return {
        'statusCode': 200,
        'headers': { 
            "Access-Control-Allow-Origin": "*" 
        },
        'body': json.dumps(reservation)
    }