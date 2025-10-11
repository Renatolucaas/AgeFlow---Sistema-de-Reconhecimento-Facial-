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