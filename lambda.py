# First Lambda Function

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    s3.download.file(bucket, key, '/tmp/image.png')

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



# 2nd Lambda Function


import json
import sagemaker 
import base64
import numpy as np
import pandas as pd
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-01-03-13-22-07-084'

def lambda_handler(event, context):

    df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),columns=["a", "b", "c"])
    number = np.pi
    print(df2)
    print(number)

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    predictor = Predictor(ENDPOINT)

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    inferences = predictor.predict(image)
    
    # We return the data back to the Step Function    
    event['inferences'] = inferences.decode("utf-8")

    return {
        'statusCode': 200,
        'body': {
            "inferences": event['inferences']
        }
    }


# The third function

import json
import ast


THRESHOLD = .93


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = ast.literal_eval(event['inferences'])
    inference = inferences[0]

    # Check if any values in our inferences are above THRESHOLD
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if inference >= THRESHOLD:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }