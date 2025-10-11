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

         # Decodificar imagem base64
        image_bytes = base64.b64decode(image_data.split(',')[1])

        # Gerar ID único
        request_id = str(uuid.uuid4())
        timestamp = int(datetime.now().timestamp())

        # Nome do arquivo no S3
        file_name = f"uploads/{request_id}.jpg"