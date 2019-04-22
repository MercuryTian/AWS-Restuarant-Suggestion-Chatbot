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

     ![es_date](/Users/macbook/Desktop/Master 1/9223A-CC/Assignment 2/README/es_date.png)

   - response:

     ![es_response](/Users/macbook/Desktop/Master 1/9223A-CC/Assignment 2/README/es_response.png)

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



