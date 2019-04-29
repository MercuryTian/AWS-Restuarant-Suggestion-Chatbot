# Chatbot Restaurant Recommendation - AWS

##### Zhengxi Tian - zt586



## Description

This is a Restaurant Suggestion Restaurant Chatbot based on AWS.

1. S3 bucket link where the chatbot app is hosted

   ```
   https://userlogin.auth.us-east-1.amazoncognito.com//login?response_type=token&client_id=4cjq38p0p3rf8tgltccbg22vh7&redirect_uri=https://s3.amazonaws.com/test1-cc/chatbox.html
   ```

2. ElasticSearch endpoint

   ```
   https://search-chatbot-najlxvv2ws7iy4mnqwtniy2ori.us-east-1.es.amazonaws.com
   ```

3. Github URL

   ```
   https://github.com/MercuryTian/AWS-Restuarant-Suggestion-Chatbot
   ```



## Features

- Sign up for new user
- Login and logout
- Real-time chat and response for the requirements
- Reservation confirm by sending email or text message.
- Using machine learning to recommend restaurants to users.



## AWS Services

- Authentication with **Amazon Cognito User Pools**.
- Serverless computing with **AWS Lambda**.
- API access control provided by **Amazon API Gateway**.
- Static site hosting on **Amazon S3**.
- Create chatbot using the **Amazon Lex** service.
- Restaurants information are stored in **DynamoDB**.
- Searching engine dirved by **ElasticSerach**.
- User requests are waiting in **SQS**.
- Sending confirmation message by **SES** or **SNS**.
- Using **SageMaker** for machine learning training and recommendation.



## Preparing Datasets - Yelp API

1. Log into Yelp Fusion: <https://www.yelp.com/developers/v3/manage_app>

- Client ID: `OY9bhzgAA-Uo0FfcOdtyDQ`

- API Key:

  ```python
  uBpXVxM8QNSEnw935kDBbR8z1GrcKpwerIm8R4eAUB3dH4c9oKPvJaFxDx4wPtSEyXy7P0fHUtcCp-_MWmxvUZsjZBaLQeJN5SlETF0OAT8WWWy-bQoD_srDAdyrXHYx
  ```

2. To authenticate API calls with the API Key, set the `Authorization` HTTP header value as `Bearer API_KEY`

3. Send GET request with basic URL `https://api.yelp.com/v3/businesses/search`

4. Clean data by writing python script.

   ```python
   import json
   
   with open("japanese.json", 'r') as data_file:
       data = json.load(data_file)
   
   for element in data['businesses']:
       element.pop("rating")
       element.pop("alias")
       element.pop("url")
       element.pop("is_closed")
       element.pop("review_count")
       element.pop("image_url")
       element.pop("phone")
       element.pop("display_phone")
       element.pop("distance")
       element.pop("transactions")
   
   # new_file = {"chinese": []}
   # new_file["chinese"] = data["businesses"]
   
   with open("yelp_restaurant.json", 'r') as data_file:
       yelp = json.load(data_file)
   yelp["japanese"] = data["businesses"]
   with open("yelp_restaurant.json", 'w') as data_file:
       data = json.dump(yelp, data_file)
   ```



## DynamoDB

1. Get access to DynamoDB by attaching exisiting policy directly to IAM.

2. Install AWS CLI in a virtual environment. (<https://docs.aws.amazon.com/cli/latest/userguide/install-virtualenv.html>)

   - Open the virtual environment: `source ~/cli-ve/bin/activate`
   - Configuration: `aws configure`
     - AWS Access Key ID
     - AWS Secret Access Key
     - Default region name: east-region-1
     - Default output format
   - Install boto3: `pip install boto3`
   - Terminate the virtual environment: `deactivate`

3. Create table `yelp-restaurants` and import yelp data (.json) into the table.

   Run the `createTable.py` under vitual environment.

   ```python
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
   ```




## Machine Learning for Recommendation - SageMaker

1. Prepare the general dataset `FILE_1.csv`, including the neccessary features:

   - restaurant_id
   - cuisine
   - rating
   - review_count

   recommend : not_recommend : all = 1 : 1 : 5

2. Labeling training datasets recommendated restaurant. Combining the recommended dataset `FEIL_2` and not-recommended dataset `FILE_3` together while shuffling into `FILE_2`. 

3. Removing the rows in `FILE_2` from `FILE_1`.

4. Configuring Jupyter notebook in SageMaker

   - Get the an Amazon Sagemaker Boto 3 Client

   ```python
   ### --- SageMaker XGBoost Algorithm --- ###
   
   import os
   import boto3
   import re
   from sagemaker import get_execution_role
   
   role = get_execution_role()
   region = boto3.Session().region_name
   
   bucket='chatbot-sagemaker-input' # put your s3 bucket name here, and create s3 bucket
   prefix = 'datasets'
   # customize to your bucket where you have stored the data
   bucket_path = 'https://s3-{}.amazonaws.com/{}'.format(region,bucket)
   ```

   - Get the Amazon SageMaker Execution Role

   ```
   
   ```

5. SageMaker XGBoost algorithm

   ```python
   from sagemaker.amazon.amazon_estimator import get_image_uri
   container = get_image_uri(region, 'xgboost')
   ```

   ```python
   # train model
   
   import boto3
   from time import gmtime, strftime
   
   job_name = 'chatbot-xgboost-regression-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
   print("Training job", job_name)
   
   #Ensure that the training and validation data folders generated above are reflected in the "InputDataConfig" parameter below.
   
   create_training_params = \
   {
       "AlgorithmSpecification": {
           "TrainingImage": container,
           "TrainingInputMode": "File"
       },
       "RoleArn": role,
       "OutputDataConfig": {
           "S3OutputPath": bucket_path + "/" + prefix + "/output"
       },
       "ResourceConfig": {
           "InstanceCount": 1,
           "InstanceType": "ml.m4.4xlarge",
           "VolumeSizeInGB": 5
       },
       "TrainingJobName": job_name,
       "HyperParameters": {
           "max_depth":"5",
           "eta":"0.2",
           "gamma":"4",
           "min_child_weight":"6",
           "subsample":"0.7",
           "silent":"0",
           "objective":"reg:linear",
           "num_round":"50"
       },
       "StoppingCondition": {
           "MaxRuntimeInSeconds": 3600
       },
       "InputDataConfig": [
           {
               "ChannelName": "train",
               "DataSource": {
                   "S3DataSource": {
                       "S3DataType": "S3Prefix",
                       "S3Uri": bucket_path + "/" + prefix + '/train',
                       "S3DataDistributionType": "FullyReplicated"
                   }
               },
               "ContentType": "text/csv",
               "CompressionType": "None"
           }
       ]
   }
   
   client = boto3.client('sagemaker', region_name=region)
   client.create_training_job(**create_training_params)
   
   import time
   
   status = client.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
   print(status)
   while status !='Completed' and status!='Failed':
       time.sleep(60)
       status = client.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
       print(status)
   ```

   ```python
   # import model into hosting
   
   import boto3
   from time import gmtime, strftime
   
   model_name=job_name + '-model'
   print(model_name)
   
   info = client.describe_training_job(TrainingJobName=job_name)
   model_data = info['ModelArtifacts']['S3ModelArtifacts']
   print(model_data)
   
   primary_container = {
       'Image': container,
       'ModelDataUrl': model_data
   }
   
   create_model_response = client.create_model(
       ModelName = model_name,
       ExecutionRoleArn = role,
       PrimaryContainer = primary_container)
   
   print(create_model_response['ModelArn'])
   ```

   ```
   chatbot-xgboost-regression-2019-04-26-21-50-59-model
   https://s3-us-east-1.amazonaws.com/chatbot-sagemaker-input/datasets/output/chatbot-xgboost-regression-2019-04-26-21-50-59/output/model.tar.gz
   arn:aws:sagemaker:us-east-1:066177567294:model/chatbot-xgboost-regression-2019-04-26-21-50-59-model
   ```

   ```python
   # create endpoint configuration
   from time import gmtime, strftime
   
   endpoint_config_name = 'chatbot-XGBoostEndpointConfig-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
   print(endpoint_config_name)
   create_endpoint_config_response = client.create_endpoint_config(
       EndpointConfigName = endpoint_config_name,
       ProductionVariants=[{
           'InstanceType':'ml.t2.medium',
           'InitialVariantWeight':1,
           'InitialInstanceCount':1,
           'ModelName':model_name,
           'VariantName':'AllTraffic'}])
   
   print("Endpoint Config Arn: " + create_endpoint_config_response['EndpointConfigArn'])
   ```

   ```
   chatbot-XGBoostEndpointConfig-2019-04-26-21-55-33
   Endpoint Config Arn: arn:aws:sagemaker:us-east-1:066177567294:endpoint-config/chatbot-xgboostendpointconfig-2019-04-26-21-55-33
   ```

   ```python
   # create endpoint
   import time
   
   endpoint_name = 'chatbot-XGBoostEndpoint-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
   print(endpoint_name)
   create_endpoint_response = client.create_endpoint(
       EndpointName=endpoint_name,
       EndpointConfigName=endpoint_config_name)
   print(create_endpoint_response['EndpointArn'])
   
   resp = client.describe_endpoint(EndpointName=endpoint_name)
   status = resp['EndpointStatus']
   print("Status: " + status)
   
   while status=='Creating':
       time.sleep(60)
       resp = client.describe_endpoint(EndpointName=endpoint_name)
       status = resp['EndpointStatus']
       print("Status: " + status)
   
   print("Arn: " + resp['EndpointArn'])
   print("Status: " + status)
   
   ```

   ```
   chatbot-XGBoostEndpoint-2019-04-26-21-55-39
   arn:aws:sagemaker:us-east-1:066177567294:endpoint/chatbot-xgboostendpoint-2019-04-26-21-55-39
   Status: Creating
   Status: Creating
   Status: Creating
   Status: Creating
   Status: Creating
   Status: Creating
   Status: Creating
   Status: Creating
   Status: InService
   Arn: arn:aws:sagemaker:us-east-1:066177567294:endpoint/chatbot-xgboostendpoint-2019-04-26-21-55-39
   Status: InService
   
   ```

   ```python
   # validate model for use
   runtime_client = boto3.client('runtime.sagemaker', region_name=region)
   
   ```

   ```python
   !wget https://s3.amazonaws.com/chatbot-sagemaker-input/datasets/FILE_1_new.csv
   
   ```

   ```
   --2019-04-26 22:05:22--  https://s3.amazonaws.com/chatbot-sagemaker-input/datasets/FILE_1_new.csv
   Resolving s3.amazonaws.com (s3.amazonaws.com)... 52.216.111.53
   Connecting to s3.amazonaws.com (s3.amazonaws.com)|52.216.111.53|:443... connected.
   HTTP request sent, awaiting response... 200 OK
   Length: 1602 (1.6K) [text/csv]
   Saving to: ‘FILE_1_new.csv.1’
   
   FILE_1_new.csv.1    100%[===================>]   1.56K  --.-KB/s    in 0s      
   
   2019-04-26 22:05:23 (112 MB/s) - ‘FILE_1_new.csv.1’ saved [1602/1602]
   
   ```

   ```python
   # test a single prediction
   !head -1 FILE_1_new.csv > chatbot.single.test
   
   ```

   ```python
   !head -1 chatbot.single.test
   
   ```

   ```python
   import json
   from itertools import islice
   import math
   import struct
   
   file_name = 'chatbot.single.test' # customize to your test file
   # with open(file_name, 'r') as f:
   #     payload = f.read()
   
   f = open("chatbot.single.test", 'r')
   payload = f.read()
   # f.seek(0)
   # payload = f.read()
   
   response = runtime_client.invoke_endpoint(EndpointName=endpoint_name, 
                                      ContentType='text/csv', 
                                      Body=payload)
   result = response['Body'].read()
   result = result.decode("utf-8")
   result = result.split(',')
   result = [math.ceil(float(i)) for i in result]
   label = payload.strip(' ').split()[0]
   print ('Label: ',label,'\nPrediction: ', result[0])
   f.close()
   
   ```

   ```python
   # test a batch of data
   import sys
   import math
   
   def do_predict(data, endpoint_name, content_type):
       payload = '\n'.join(data)
       response = runtime_client.invoke_endpoint(EndpointName=endpoint_name, 
                                      ContentType=content_type, 
                                      Body=payload)
       result = response['Body'].read()
       result = result.decode("utf-8")
       result = result.split(',')
       preds = [float((num)) for num in result]
       preds = [math.ceil(num) for num in preds]
       return preds
   
   def batch_predict(data, batch_size, endpoint_name, content_type):
       items = len(data)
       arrs = []
       
       for offset in range(0, items, batch_size):
           if offset+batch_size < items:
               results = do_predict(data[offset:(offset+batch_size)], endpoint_name, content_type)
               arrs.extend(results)
           else:
               arrs.extend(do_predict(data[offset:items], endpoint_name, content_type))
           sys.stdout.write('.')
       return(arrs)
   
   ```

   ```python
   import json
   import numpy as np
   
   with open('FILE_1_new.csv', 'r') as f:
       payload = f.read().strip()
   
   # labels = [int(line.split(' ')[0]) for line in payload.split('\n')]
   test_data = [line for line in payload.split('\n')]
   preds = batch_predict(test_data, 100, endpoint_name, 'text/csv')
   
   print(preds)
   # print('\n Median Absolute Percent Error (MdAPE) = ', np.median(np.abs(np.array(labels) - np.array(preds)) / np.array(labels)))
   
   ```

   ```python
   # delete endpoint once finish
   client.delete_endpoint(EndpointName=endpoint_name)
   ```



## ElasticSearch

1. Create an ElasticSearch domain - `chatbot`

2. Modify access policy as follows to avoid authorization error:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "*"
         },
         "Action": "es:*",
         "Resource": "arn:aws:es:us-east-1:ACCOUNT_ID:domain/chatbot/*"
       }
     ]
   }
   ```

3. Create index and type in ElasticSearch via Postman.

   - `POST` request: 

     ```json
     https://search-chatbot-najlxvv2ws7iy4mnqwtniy2ori.us-east-1.es.amazonaws.com/restaurants/Restaurant/_bulk
     ```

   - index: `restaurants`

   - type: `Restaurant`

   - `_bulk`: for multiple "actions" in one query you should use the [Bulk API](http://www.elastic.co/guide/en/elasticsearch/reference/1.3/docs-bulk.html)

   - body:

     - Keep `name` attribute just for verification.

     - Notice the format of JSON data and have to add a trailing newline.

     ![es_data](/Users/macbook/Desktop/Master 1/9223A-CC/Assignment 2/AWS-Restuarant-Suggestion-Chatbot-master/README/es_data.png)

   - response:

     ![es_response](/Users/macbook/Desktop/Master 1/9223A-CC/Assignment 2/AWS-Restuarant-Suggestion-Chatbot-master/README/es_response.png)

4. Search `cuisine` or `restaurant name` in ElasticSearch

   - `GET` request:

     ```json
     https://search-chatbot-najlxvv2ws7iy4mnqwtniy2ori.us-east-1.es.amazonaws.com/restaurants/Restaurant/_search?q=chinese
     ```

   - `q`: search for one specific key word



## Lambda Function 2 - SNS

1. Create a standard SQS called `requests` to store the requests from users, which derived from Lambda `getMessage` function.

2. Trigger logistic:

   LF1 (`getMessage`) send requests  ->  SQS  ->  trigger LF2 (`queueWorker`) -> send reserations by SNS

3. Push the requests collected from the user to the SQS `request` queue. Implemented in LF1 `getMessage`.

   ```python
   # Send the requests from users to the SQS
   sqs = boto3.resource('sqs')
   queue = sqs.get_queue_by_name(QueueName = "requests") # get the URL of SQS
   if location and cuisine and number_people and dining_date and dining_time and email:
     queue_response = queue.send_message(MessageBody = suggestion)
     print("SUCESSFULLY SENDING TO SQS")
   ```

4. Configure a trigger for LF2 `queueworker` and whenever it is invoked:

   - Pulls a message from the SQS queue .

   - Gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB.

   - Formats them.

   - Sends them over text message to the phone number included in the SQS message, using SNS or SES.

   - After processing the request, pop it fro the SQS queue.

5. SNS

   - Create a Topic named `restaurantReservation`
   - Create a `SNS` client and send message to the phone number.

   ```python
   ### --- send email confirmation by SNS --- ###
   phone_number = req["phone_number"]
   
   # send SMS message
   sns = boto3.client('sns')
   
   sns.publish(
   	PhoneNumber=phone_number,
   	Message=reservation
   )
   ```

6. SES

   - Verify new emails address for sending and receiving messages.
   - Create a `SES` client and send message to the email address.

   ```python
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
   ```

7. Changing the Lex and LF1 `getMessage` to meet the new requirement.





# Assigntment 1



## S3 Bucket

1. Create bucket

2. Add a bucket policy to make bucket content publicly available

   If cannot add bucket policy, check `Manage public access control lists (ACLs)` and turn them to False.

3. Upload `chatbot.html` and javascript SDK to S3, then make public resources in S3. The main codes include in S3 folder are `chatbot.html` and `apiGateway-js-sdk`.



## Swagger

Specification: OpenAPI Specification, an API description format for REST APIs.

Syntax: `YAML`

Version: `Swagger 2.0`

#### Parameter Description

**1. chabot:** `/chatbot`

- $POST: send message
- $GET: get message



## API Gateway

1. Upload swagger API to the API Gateway: [AI Customer Service API](https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis/1jdb55uq51/resources)
2. Create lambda function for each REST API, connect API Gateway with Lambda.
   - Test API and lambda functions.
   - Watch testing logs via CloudWatch.
3. Add IAM authorization on `Method Request`.
4. Enable CORS on API methods.
5. Deploy API in `Actions` and generate SDK for API

- Install, initiate and call a JavaScript SDK generated by API Gateway for a REST API.

- Create a API key first:

  `flx55nycvg`

  ![API-key](/Users/macbook/Desktop/Master%201/9223A-CC/Assignment%201/AWS-Restuarant-Suggestion-Chatbot-master/README/API-key.png)

- Include references to the following scripts:

  ```html
  <script type="text/javascript" src="lib/axios/dist/axios.standalone.js"></script>
  <script type="text/javascript" src="lib/CryptoJS/rollups/hmac-sha256.js"></script>
  <script type="text/javascript" src="lib/CryptoJS/rollups/sha256.js"></script>
  <script type="text/javascript" src="lib/CryptoJS/components/hmac.js"></script>
  <script type="text/javascript" src="lib/CryptoJS/components/enc-base64.js"></script>
  <script type="text/javascript" src="lib/url-template/url-template.js"></script>
  <script type="text/javascript" src="lib/apiGatewayCore/sigV4Client.js"></script>
  <script type="text/javascript" src="lib/apiGatewayCore/apiGatewayClient.js"></script>
  <script type="text/javascript" src="lib/apiGatewayCore/simpleHttpClient.js"></script>
  <script type="text/javascript" src="lib/apiGatewayCore/utils.js"></script>
  <script type="text/javascript" src="apigClient.js"></script>
  ```

- To use an API key with the SDK generated by API Gateway, pass the API key as a parameter to the `Factory` object by using code similar to the following. If you use an API key, it is specified as part of the `x-api-key` header and all requests to the API will be signed. This means you must set the appropriate CORS Accept headers for each request.

  ```javascript
  // Initialize the SDK for API Gateway
  // Use API key, have to set the appropriate CORS Accept headers for each request
          var apigClient = apigClientFactory.newClient({
              apiKey: 'flx55nycvg';  // this is the API_key for 'chatbot'
          });
  ```

- Call the API methods in API Gateway by using code similar to the following. Each call returns a promise with a success and failure callbacks.

- `apigClient.js` file, main codes are shown below:

  - Set app client:

  ```javascript
  var apigClientFactory = {};
  apigClientFactory.newClient = function (config) {
      var apigClient = { };
      if(config === undefined) {
          config = {
              accessKey: 'chatbot',
              secretKey: 'zt586@nyu.edu',
              sessionToken: '',
              region: 'us-east-1',
              apiKey: undefined,
              defaultContentType: 'application/json',
              defaultAcceptType: 'application/json'
          };
      }
  ```

  - Call `$GET` API:

  ```javascript
  apigClient.chatbotGet = function (params, body, additionalParams) {
          if(additionalParams === undefined) { additionalParams = {}; }
          
          apiGateway.core.utils.assertParametersDefined(params, [], ['body']);
          
          var chatbotGetRequest = {
              verb: 'get'.toUpperCase(),
              path: pathComponent + uritemplate('/chatbot').expand(apiGateway.core.utils.parseParametersToObject(params, [])),
              headers: apiGateway.core.utils.parseParametersToObject(params, []),
              queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
              body: body
          };
          
          
          return apiGatewayClient.makeRequest(chatbotGetRequest, authType, additionalParams, config.apiKey);
      };
  ```

  - Call `$ POST` API:

  ```javascript
  apigClient.chatbotPost = function (params, body, additionalParams) {
          if(additionalParams === undefined) { additionalParams = {}; }
          
          apiGateway.core.utils.assertParametersDefined(params, ['body'], ['body']);
          
          var chatbotPostRequest = {
              verb: 'post'.toUpperCase(),
              path: pathComponent + uritemplate('/chatbot').expand(apiGateway.core.utils.parseParametersToObject(params, [])),
              headers: apiGateway.core.utils.parseParametersToObject(params, []),
              queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
              body: body
          };
          
          
          return apiGatewayClient.makeRequest(chatbotPostRequest, authType, additionalParams, config.apiKey);
      };
  ```



## Lambda Function (LF0 & LF1)

1. Give credentials to the role in lambda function via IAM.
2. Author a Python lambda function from scratch。
   - Select `Author from scratch`. Create a name for the lambda function.
   - Change runtime to `Python 3.6`.
   - Create a new Role from template or create custom role in the IAM console. As for the policy option, we can leave it present and add policies later in IAM.
3. Amazon CloudWatch Logs

- Watching testing logs for Lambda and API Gateway.

4. Integrate LF0 `sendMessage`  with Lex, using `POST_TEXT` method in  ` boto3`.

   ```python
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
   ```

5. Lambda (LF1) used to interact with Lex and call external Yelp API. 




## Cognito

1. Manage user pools

   - Create a user pool.

   - Review default settings to create a user pool.

     ```bash
     Pool Id: us-east-1_KMfefSLmw
     Pool ARN: arn:aws:cognito-idp:us-east-1:066177567294:userpool/us-east-1_KMfefSLmw
     ```

2. Add an app client in user pool

- App client settings: 

  - Sign-in and sign-out URL settings: set sign-in URL here to complete the sign-in process of chatbot.
  - OAuth 2.0: 
    - [x] Authorization code grant
    - [x] implicit grant: which will give the JWT tokens
    - [x] Allowed OAuth scope: email...

- Create an Amazon cognito domain

  `http://userlogin.auth.us-east-1.amazoncognito.com`

- Type the domain in a new web page

  - Add in the following: 

    `/login?response_type=token&client_id=4cjq38p0p3rf8tgltccbg22vh7&redirect_uri=https://s3.amazonaws.com/test1-cc/chatbox.html`

    - `client_id` is the App client ID shows in the left side.
    - `redirect_uri` is the callable URL in sign-in part.

  - If you want the code response: `/login?response_type=code`

3. Log-in web page

```html
https://userlogin.auth.us-east-1.amazoncognito.com//login?response_type=token&client_id=4cjq38p0p3rf8tgltccbg22vh7&redirect_uri=https://s3.amazonaws.com/test1-cc/chatbox.html
```

![sign-in](/Users/macbook/Desktop/Master%201/9223A-CC/Assignment%201/AWS-Restuarant-Suggestion-Chatbot-master/README/sign-in.png)

4. Identity Pool:

   - Giving identity credentials in `chatbot.html`:

     ```javascript
     function parseJwt (token) {
                 var base64Url = token.split('.')[1];
                 var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                 return window.atob(base64);
             };
     		// set the focus to the input box
     		document.getElementById("wisdom").focus();
     
     		// Initialize the Amazon Cognito credentials provider
     		var token = window.location.hash.split('&')[0].split('=')[1]
     
     		var accessKeyId;
     		var secretAccessKey;
     		var sessionToken;
     
     		AWS.config.region = 'us-east-1';
     		
     		// Configure the credentials provider to use your identity pool
     		// AWS.config.credentials = new AWS.CognitoIdentityCredentials({
     		myCredentials = new AWS.CognitoIdentityCredentials({
     			IdentityPoolId: 'us-east-1:46e47174-cb7a-4a50-a055-4a86158460b8',
     			Logins: {
     					'cognito-idp.us-east-1.amazonaws.com/us-east-1_KMfefSLmw': token
     				}
     		});
     
     ```

   - Adding `"Access-Control-Allow-Origin"` in headler in Lambda:

     ```javascript
     return {
             'statusCode': 200,
             'headers': { 
                 "Access-Control-Allow-Origin": "*" 
             },
             'body': json.dumps(response)
         }
     
     ```



## Lex

1. Intent contains:

- GreetingIntent
- ThankYouIntent
- DiningSuggestionsIntent: Integrating `DiningSuggestionIntent` with LF1.

![dinningIntent](/Users/macbook/Desktop/Master%201/9223A-CC/Assignment%201/AWS-Restuarant-Suggestion-Chatbot-master/README/dinningIntent.png)

2. To start conversation:

- Utterance to trigger **GreetingIntent**
  - Hi
  - Hello
  - I need some restaurant suggestions
- Utterance to trigger **DiningSuggestionsIntent**
  - I need help.
  - I don't know where to eat.
  - I need some restaurant suggestions.
- Utterance to trigger **ThankYouIntent**
  - Thanks
  - Thank you
  - Thanks for your help



