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

        # Upload para S3
        s3.put_object(
            Bucket='age-estimation-system-dev-images',
            Key=file_name,
            Body=image_bytes,
            ContentType='image/jpeg',
            Metadata={
                'requestId': request_id,
                'userEmail': user_email,
                'timestamp': str(timestamp)
            }
        )

        # Mensagem para a fila
        queue_message = {
            'requestId': request_id,
            's3Key': file_name,
            'userEmail': user_email,
            'timestamp': timestamp
        }

        # Enviar para SQS
        sqs.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/age-estimation-system-dev-upload-queue',
            MessageBody=json.dumps(queue_message)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'requestId': request_id,
                'message': 'Imagem recebida e em processamento'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }