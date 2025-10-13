import boto3
import sys
import os

def test_aws_connection():
    """Testar conexão com serviços AWS"""
    services_to_test = [
        ('rekognition', 'list_collections'),
        ('s3', 'list_buckets'),
        ('sts', 'get_caller_identity')
    ]
    
    print("🔍 Testando conexão AWS...")
    
    for service_name, method_name in services_to_test:
        try:
            client = boto3.client(service_name, region_name='us-east-2')
            method = getattr(client, method_name)
            
            if service_name == 'rekognition':
                result = method(MaxResults=5)
                print(f"✅ Rekognition - Coleções: {len(result.get('CollectionIds', []))}")
            elif service_name == 's3':
                result = method()
                print(f"✅ S3 - Buckets: {len(result.get('Buckets', []))}")
            elif service_name == 'sts':
                result = method()
                print(f"✅ STS - Usuário: {result['Arn']}")
                
        except Exception as e:
            print(f"❌ {service_name.upper()} - Erro: {str(e)}")
    
    print("\n📋 Próximos passos:")
    print("1. Configure credenciais AWS")
    print("2. Execute: python scripts/setup.py")
    print("3. Teste: python backend/simple_processor.py")

if __name__ == "__main__":
    test_aws_connection()