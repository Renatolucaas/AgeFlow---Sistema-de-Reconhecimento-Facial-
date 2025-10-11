import json
import boto3
from datetime import datetime

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            # Processar mensagem da fila
            message = json.loads(record['body'])
            request_id = message['requestId']
            s3_key = message['s3Key']
            user_email = message['userEmail']

              # Buscar imagem do S3
            s3_response = s3.get_object(
                Bucket='age-estimation-system-dev-images',
                Key=s3_key
            )
            image_bytes = s3_response['Body'].read()

            # Chamar Amazon Rekognition para detecção facial
            rekognition_response = rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )

             # Processar resultados
            results = process_faces(rekognition_response, request_id)
            
            # Salvar no DynamoDB
            save_to_dynamodb(results, user_email)

            # Enviar para fila de resultados
            send_to_results_queue(results, user_email)
            
            print(f"Processamento concluído para {request_id}")
            
        except Exception as e:
            print(f"Erro no processamento: {str(e)}")
            continue

def process_faces(rekognition_response, request_id):
    faces_data = []
    
    for i, face_detail in enumerate(rekognition_response['FaceDetails']):
        age_range = face_detail['AgeRange']
        emotions = face_detail['Emotions']
        gender = face_detail['Gender']