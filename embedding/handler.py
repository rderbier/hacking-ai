import json
import os
os.environ['TRANSFORMERS_CACHE'] = '/tmp'
from sentence_transformers import SentenceTransformer

# change CACHE else we get following error at runtime in AWS Lambda:
# There was a problem when trying to write in your cache folder (/home/sbx_user1051/.cache/huggingface/hub).

model = SentenceTransformer('/var/task/model')

def handler(event, context):
    # source = event.get('source')
    # type = event.get('detail-type')
    # if source == 'aws.events' and type == 'Scheduled Event': 
    #    return {"statusCode": 200, "body": "Lambda is warm!"}
    
    body = json.loads(event['body'])
    replyKserve = False
    if isinstance(body, dict):
        if 'instances' in body:
            print("body contains 'instances'")
            replyKserve = True
            sentences = body['instances']
        else:
            print("body is a map of uids and sentences")
            replyKserve = False
            sentences = [body[key] for key in body]
    else:
        # return unprocessable entity
        return {
            "statusCode": 422,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type,X-Api-Key",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            }
        }
    
    embeddings = model.encode(sentences)
    if replyKserve == False:
        keylist = list(body.keys())
        resp = {keylist[i]:json.dumps(embeddings[i].tolist()) for i in range(len(embeddings))}
    else:
        resp = { "predictions": embeddings.tolist()}

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type,X-Api-Key",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        }, 
        "body": json.dumps(resp)
        }

