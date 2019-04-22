import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.client('dynamodb')
    
    response = dynamodb.get_item(
        TableName='yelp-restaurants',
        Key={
            'cuisine': {
                'S': 'chinese'
            },
            'id': {
                'S': 'ojbH3wnRu050hRhkmoxRiA'
            }
        }
    )
    print(json.dumps(response))
    
    return {
        'statusCode': 200,
        'headers': { 
            "Access-Control-Allow-Origin": "*" 
        },
        'body': json.dumps(response)
    }

""" queueWorker TEST
{
  "Records": [
    {
      "messageId": "6c5cf179-d339-483f-83ab-21d6effbe4fa",
      "receiptHandle": "AQEBD2ramQfBE02QEJkhv2iZTTH/5P+BDBA8ZewrhZZy5hxla9Yw7GDJJw1D7AVSa9PsTMDZbYrX7grq008X8rDufGArTWTIIb8VPmoOB5M0H1NldwQy2mQz6ULUFuhBUAnNzsCG9QiiqiY+nqXLkmFnks9F8HujvTnAvsh+Cnkxqf8uRUiQurVWNLEzSXrRbZV+Mezc0xZIS2kibyqnwQaOw+KWY9bYS+9rc/LgmA5a4z4hjL9m56lAMh+QKZbwlctdsgexPnaKD/lJ9CW9ipiSw1/bPlY9NSLTCspbXTgZXPKtPPI7w+3bPAgRu3LW6iQGoWDWJvJSKM/MZ/2Oh1VobrJtNz2eZf0642smCjWM3np49Kpvm+dKhLi0YByqNim0",
      "body": "{\"location\": \"New York\", \"cuisine\": \"Chinese\", \"number_people\": \"2\", \"dining_date\": \"2019-04-19\", \"dining_time\": \"19:00\", \"phone_number\": \"3472214796\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1555633765253",
        "SenderId": "AROAIRN5RAPMCUBDIZWPG:getMessage",
        "ApproximateFirstReceiveTimestamp": "1555633765256"
      },
      "messageAttributes": {},
      "md5OfBody": "0e3abc581385f02bc4809a108525d928",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:066177567294:requests",
      "awsRegion": "us-east-1"
    }
  ]
}
"""