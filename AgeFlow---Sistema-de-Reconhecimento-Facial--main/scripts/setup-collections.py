import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

def setup_rekognition_collection():
    try:
        # Configurar cliente Rekognition
        rekognition = boto3.client('rekognition', region_name='us-east-2')  # ← Corrigir para us-east-2
        
        # Verificar credenciais
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Credenciais válidas - Usuário: {identity['Arn']}")
        
        # Criar coleção para faces conhecidas (opcional)
        try:
            response = rekognition.create_collection(
                CollectionId='age-estimation-faces'
            )
            print("✅ Coleção Rekognition criada:", response['CollectionArn'])
        except rekognition.exceptions.ResourceAlreadyExistsException:
            print("ℹ️ Coleção já existe")
        
        # Listar coleções existentes
        collections = rekognition.list_collections()
        print("📋 Coleções disponíveis:", collections['CollectionIds'])
        
        return True
        
    except NoCredentialsError:
        print("❌ ERRO: Credenciais AWS não encontradas")
        print("\n📝 Como configurar:")
        print("1. Execute: aws configure")
        print("2. Ou defina variáveis de ambiente:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY") 
        print("   - AWS_DEFAULT_REGION")
        return False
        
    except ClientError as e:
        print(f"❌ Erro AWS: {e.response['Error']['Message']}")
        return False

if __name__ == "__main__":
    print("🔧 Configurando ambiente AWS Rekognition...")
    success = setup_rekognition_collection()
    
    if success:
        print("\n🎉 Configuração concluída com sucesso!")
    else:
        print("\n💡 Dica: Verifique se você tem permissões para:")
        print("   - rekognition:CreateCollection")
        print("   - rekognition:ListCollections")