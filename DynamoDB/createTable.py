from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from datetime import *

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

### create table ###

table = dynamodb.create_table(
    TableName='yelp-restaurants',

    KeySchema = [
        {
            'AttributeName': 'cuisine',
            'KeyType': 'HASH' # The values of two partition keys could be the same
        },
        {
            'AttributeName': 'id',
            'KeyType': 'RANGE'
        }
    ],

    AttributeDefinitions=[
        {
            'AttributeName': 'cuisine',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],

    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print("Table status:", table.table_status)


### import JSON to items ###
table = dynamodb.Table('yelp-restaurants')

with open("yelp1.json", 'r') as json_file:
    data = json.load(json_file, parse_float = decimal.Decimal)
    for restaurant in data:
        cuisine = restaurant["cuisine"]
        ID = restaurant["id"]
        name = restaurant["name"]
#         price = restaurant["price"]
        coord = "coordinates are not available" if "coordinates" not in restaurant else restaurant["coordinates"]
        location = "location is not available" if "location" not in restaurant else restaurant["location"] 
        cate = "categories are not available" if "categories" not in restaurant else restaurant["categories"]

        table.put_item(
            Item = {
                'cuisine': cuisine,
                'id': ID,
                'name': name,
                'coordinates': coord,
                'location': location,
                'categories': cate,
                'insertedAtTimestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }       
        )