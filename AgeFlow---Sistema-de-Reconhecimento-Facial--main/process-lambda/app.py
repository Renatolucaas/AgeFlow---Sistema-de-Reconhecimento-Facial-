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

        # Encontrar emoção predominante
        primary_emotion = max(emotions, key=lambda x: x['Confidence'])
        
        face_data = {
            'faceId': f"{request_id}-face-{i}",
            'ageRange': {
                'low': age_range['Low'],
                'high': age_range['High'],
                'estimated': (age_range['Low'] + age_range['High']) // 2
            },
            'gender': {
                'value': gender['Value'],
                'confidence': gender['Confidence']
            },
            'emotion': {
                'type': primary_emotion['Type'],
                'confidence': primary_emotion['Confidence']
            },
            'timestamp': int(datetime.now().timestamp())
        }
        faces_data.append(face_data)
    
    return {
        'requestId': request_id,
        'facesDetected': len(faces_data),
        'faces': faces_data,
        'processedAt': datetime.now().isoformat()
    }

def save_to_dynamodb(results, user_email):
    table = dynamodb.Table('age-estimation-system-dev-results')
    
    item = {
        'requestId': results['requestId'],
        'timestamp': results['faces'][0]['timestamp'] if results['faces'] else int(datetime.now().timestamp()),
        'userEmail': user_email,
        'facesDetected': results['facesDetected'],
        'faces': results['faces'],
        'processedAt': results['processedAt']
    }
    
    table.put_item(Item=item)

def send_to_results_queue(results, user_email):
    message = {
        'requestId': results['requestId'],
        'userEmail': user_email,
        'results': results
    }
    
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/age-estimation-system-dev-results-queue',
        MessageBody=json.dumps(message)
    )