import json
from datetime import *
import boto3

def lambda_handler(event, context):
    """
    This function is aim to implement the function of sending messages
    """
    client = boto3.client('lex-runtime')
    
    # print("event shows here", event, sep = '-----')
    body = event["body"]
    
    # json-fy the event first to extract
    body = json.loads(body)
    msg_cont = body["messages"][0]
   
    msg_strc = msg_cont["unstructured"]
    msg_text = msg_strc["text"]
    
    response = client.post_text(
        botName ='chatbot',
        botAlias ='zxtian',
        userId ='kelly',
        # sessionAttributes={
        #     'string': 'string'
        # },
        # requestAttributes={
        #     'string': 'string'
        # },
        inputText = msg_text
    )
    
    return_msg = response["message"]

    response = {'id': msg_strc['id'], 
                'text': return_msg, 
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")} # convert datetime to string
    
    return {
        'statusCode': 200,
        'headers': { 
            "Access-Control-Allow-Origin": "*" 
        },
        'body': json.dumps(response)
    }
