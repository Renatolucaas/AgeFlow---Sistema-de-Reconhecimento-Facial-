import json
import boto3
import uuid
import base64
from datetime import datetime

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    try:
        # Parse do corpo da requisição
        body = json.loads(event['body'])
        image_data = body['image']
        user_email = body.get('email', 'anonymous@example.com')