import json
import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            request_id = message['requestId']
            user_email = message['userEmail']
            results = message['results']
            
            # Gerar mensagem de feedback
            feedback_message = generate_feedback_message(results)