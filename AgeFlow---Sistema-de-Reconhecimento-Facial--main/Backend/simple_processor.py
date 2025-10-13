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

            # Encontrar emoção predominante
            primary_emotion = max(emotions, key=lambda x: x['Confidence'])
            
            face_data = {
                'faceId': f"face-{i}",
                'ageRange': {
                    'low': age_range['Low'],
                    'high': age_range['High'],
                    'estimated': (age_range['Low'] + age_range['High']) // 2
                },
                'gender': {
                    'value': gender['Value'],
                    'confidence': round(gender['Confidence'], 1)
                },
                'emotion': {
                    'type': primary_emotion['Type'],
                    'confidence': round(primary_emotion['Confidence'], 1)
                },
                'boundingBox': face_detail['BoundingBox']
            }
            faces_data.append(face_data)
        
        return {
            'requestId': str(uuid.uuid4()),
            'userEmail': user_email,
            'facesDetected': len(faces_data),
            'faces': faces_data,
            'processedAt': datetime.now().isoformat()
        }
    
    def process_base64_image(self, base64_data, user_email="anonymous@example.com"):
        """Processar imagem em base64"""
        try:

            # Decodificar base64
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            image_bytes = base64.b64decode(base64_data)
            return self.process_image(image_bytes, user_email)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro ao decodificar imagem: {str(e)}"
            }

# Exemplo de uso
if __name__ == "__main__":
    processor = AgeEstimationProcessor()
    
    if processor.check_credentials():
        print("🔍 Testando processamento...")
        
        # Você pode testar com uma imagem local
        # result = processor.process_image(open("test.jpg", "rb").read())
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("✅ Sistema pronto para uso!")
    else:
        print("❌ Configure as credenciais AWS primeiro")