import boto3
import json
import base64
import uuid
from datetime import datetime
from botocore.exceptions import NoCredentialsError, ClientError

class AgeEstimationProcessor:
    def __init__(self):
        self.rekognition = boto3.client('rekognition', region_name='us-east-1')
        self.s3 = boto3.client('s3')
        
    def check_credentials(self):
        """Verificar se as credenciais estão configuradas"""
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ Conectado como: {identity['Arn']}")
            return True
        except NoCredentialsError:
            print("❌ Credenciais não encontradas")
            return False
    
    def process_image(self, image_bytes, user_email="anonymous@example.com"):
        """Processar imagem e estimar idade"""
        try:
            # Chamar Amazon Rekognition
            response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )

             # Processar resultados
            results = self._process_faces(response, user_email)
            return {
                'success': True,
                'results': results
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f"Erro AWS: {e.response['Error']['Message']}"
            }
        except Exception as e:
            return {
                'success': False, 
                'error': f"Erro interno: {str(e)}"
            }
    
    def _process_faces(self, rekognition_response, user_email):
        """Processar dados das faces detectadas"""
        faces_data = []
        
        for i, face_detail in enumerate(rekognition_response['FaceDetails']):
            age_range = face_detail['AgeRange']
            emotions = face_detail['Emotions']
            gender = face_detail['Gender'] 