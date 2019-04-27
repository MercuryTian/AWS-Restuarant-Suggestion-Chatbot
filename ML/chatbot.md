

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
#         {
#             "ChannelName": "validation",
#             "DataSource": {
#                 "S3DataSource": {
#                     "S3DataType": "S3Prefix",
#                     "S3Uri": bucket_path + "/" + prefix + '/validation',
#                     "S3DataDistributionType": "FullyReplicated"
#                 }
#             },
#             "ContentType": "libsvm",
#             "CompressionType": "None"
#         }
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

    Training job chatbot-xgboost-regression-2019-04-26-21-50-59
    InProgress
    InProgress
    InProgress
    InProgress
    Completed



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

    chatbot-xgboost-regression-2019-04-26-21-50-59-model
    https://s3-us-east-1.amazonaws.com/chatbot-sagemaker-input/datasets/output/chatbot-xgboost-regression-2019-04-26-21-50-59/output/model.tar.gz
    arn:aws:sagemaker:us-east-1:066177567294:model/chatbot-xgboost-regression-2019-04-26-21-50-59-model



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

    chatbot-XGBoostEndpointConfig-2019-04-26-21-55-33
    Endpoint Config Arn: arn:aws:sagemaker:us-east-1:066177567294:endpoint-config/chatbot-xgboostendpointconfig-2019-04-26-21-55-33



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



```python
# validate model for use
runtime_client = boto3.client('runtime.sagemaker', region_name=region)
```


```python
!wget https://s3.amazonaws.com/chatbot-sagemaker-input/datasets/FILE_1_new.csv
```

    --2019-04-26 22:05:22--  https://s3.amazonaws.com/chatbot-sagemaker-input/datasets/FILE_1_new.csv
    Resolving s3.amazonaws.com (s3.amazonaws.com)... 52.216.111.53
    Connecting to s3.amazonaws.com (s3.amazonaws.com)|52.216.111.53|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 1602 (1.6K) [text/csv]
    Saving to: ‘FILE_1_new.csv.1’
    
    FILE_1_new.csv.1    100%[===================>]   1.56K  --.-KB/s    in 0s      
    
    2019-04-26 22:05:23 (112 MB/s) - ‘FILE_1_new.csv.1’ saved [1602/1602]




```python
# test a single prediction
!head -1 FILE_1_new.csv > chatbot.single.test
```


```python
!head -1 chatbot.single.test
```

    4.5,241



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

    Label:  4.5,241 
    Prediction:  1



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




    {'ResponseMetadata': {'RequestId': '09791a9b-0d7b-4179-a8e5-8f6a05909e7c',
      'HTTPStatusCode': 200,
      'HTTPHeaders': {'x-amzn-requestid': '09791a9b-0d7b-4179-a8e5-8f6a05909e7c',
       'content-type': 'application/x-amz-json-1.1',
       'content-length': '0',
       'date': 'Fri, 26 Apr 2019 22:12:17 GMT'},
      'RetryAttempts': 0}}


