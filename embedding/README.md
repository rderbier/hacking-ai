<!--
title: 'AWS Simple HTTP Endpoint example in Python'
description: 'This template demonstrates how to make a simple HTTP API with Python running on AWS Lambda and API Gateway using the Serverless'
-->
# sentence transformer exposed as a serverless AWS Lambda function

This repo provides the artefacts and steps to expose an AWS Lambda function providing vector embedding for sentences based on huggingface model.

We will expose the service as an HTTP API in an AWS Lambda service.
Embeddings are computed using a model from https://huggingface.co/sentence-transformers


## Design
We deploy a Lambda function using a custom docker image build from public.ecr.aws/lambda/python:3.8.

The docker image contains python library, sentence transformer pre-trained model and the lambda function handler.

Following https://www.philschmid.de/serverless-bert-with-huggingface-aws-lambda-docker

**Service signature**
The service accepts a map of IDs and sentences
```json
{
    "0x01":"some text",
    "0x02":"other sentence
}
```

and returns a map of IDs and vectors.
```json
{
    "0x01":"[-0.010852468200027943, -0.016728922724723816, ...]",
    ...
}
```


We opted for a map vs an array of vectors to support parallelism and async design if needed.
By using IDs, we don't have to provide the vectors in the same order as the sentences and we don't need to keep track of the input array to make sense of the output.

Client should use the IDs to associate the vectors with the right objects.




### Downloads models
export MODEL_NAME="all-minilm-l6-v2"

use a python environment with
python 3.8
transformers==4.33.1
sentence-transformers==2.2.2
pytorch==1.13
run the script ./scripts/getmodels.py


Verify that the model artefacts are created in model folder and are in the format of pytorch_model.bin

torch 2 is producing a different model format, make sure you are using the right version.


### Set your AWS CLI 
Have AWS cli installed.
Get your credentials from your AWS account.
```
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```
or use an aws profile.

### Create ECR repository
```
export aws_region=us-east-1
export aws_account_id=`aws sts get-caller-identity --query Account --output text`

export MODEL_NAME="all-minilm-l6-v2"

aws ecr create-repository --repository-name embedding-${MODEL_NAME} --region $aws_region 
```
### build and tag the docker image
```
docker build  --platform linux/arm64  --no-cache -f arm64-dockerfile -t ${MODEL_NAME}-arm64 .

docker tag ${MODEL_NAME}-arm64 $aws_account_id.dkr.ecr.us-east-1.amazonaws.com/embedding-${MODEL_NAME}
```

### push the image to ECR
```
aws ecr get-login-password --region $aws_region  \
| docker login \
    --username AWS \
    --password-stdin $aws_account_id.dkr.ecr.us-east-1.amazonaws.com/embedding-${MODEL_NAME}
Login Succeeded

docker push $aws_account_id.dkr.ecr.us-east-1.amazonaws.com/embedding-${MODEL_NAME}
```

### deploy the serverless function
Use serverless framework 3 with serverless-plugin-log-retention.


Deploy to AWS
```
$ serverless deploy 
```



_Note_: In current form, after deployment, your API is protected by an API key. 



### Invocation
```
curl --request POST \

--url https://<>.execute-api.us-east-1.amazonaws.com/dev/embedding \
--header 'Content-Type: application/json' --header 'x-api-key: <apikey>' \
--data '{"id":"some sample text"}'
```


### Local development



docker run -d --name ${MODEL_NAME}-arm64 -p 8180:8080  -v ./:/var/task/   ${MODEL_NAME}-arm64


```
curl --request POST \
--url http://localhost:8180/2015-03-31/functions/function/invocations \
--header 'Content-Type: application/json' \
--data '{"body":"{\"id1\":\"some sample text\",\"id2\":\"some other text\"\n}"}'
```



## Note
We are using pytorch wheel to reduce the size of the image:
if requirements.txt contains
https://download.pytorch.org/whl/cpu/torch-2.1.0%2Bcpu-cp311-cp311-linux_x86_64.whl

the image is 2.37GB

