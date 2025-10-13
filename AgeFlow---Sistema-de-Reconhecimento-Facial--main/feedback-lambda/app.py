import json
import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    print(f"📨 Evento recebido: {json.dumps(event)}")
    
    processed_count = 0
    error_count = 0
    
    for record in event['Records']:
        try:
            # A mensagem pode vir encoded da SQS
            if 'body' in record:
                message_body = record['body']
                
                # Se for string, fazer parse
                if isinstance(message_body, str):
                    message = json.loads(message_body)
                else:
                    message = message_body
                
                request_id = message['requestId']
                user_email = message['userEmail']
                results = message['results']
                
                print(f"📧 Processando email para: {user_email}, Request: {request_id}")
                
                # Gerar mensagem de feedback
                feedback_message = generate_feedback_message(results)
                
                # Enviar notificação via SNS
                send_notification(user_email, feedback_message, request_id)
                
                print(f"✅ Feedback enviado para {user_email}")
                processed_count += 1
                
            else:
                print("❌ Record sem body")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Erro no envio de feedback: {str(e)}")
            error_count += 1
            continue
    
    # ✅ RETORNO OBRIGATÓRIO PARA LAMBDA
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processamento concluído: {processed_count} sucesso, {error_count} erros',
            'processed': processed_count,
            'errors': error_count
        })
    }

def generate_feedback_message(results):
    faces = results['faces']
    
    if results['facesDetected'] == 0:
        return "Nenhuma face detectada na imagem. Tente com uma foto mais clara."
    
    messages = []
    messages.append(f"📊 Análise concluída! {results['facesDetected']} face(s) detectada(s).")
    
    for i, face in enumerate(faces):
        age_est = face['ageRange']['estimated']
        gender = face['gender']['value'].lower()
        emotion = face['emotion']['type'].lower()
        
        message = (
            f"👤 Face {i+1}:\n"
            f"• Faixa etária: {face['ageRange']['low']}-{face['ageRange']['high']} anos "
            f"(estimativa: {age_est} anos)\n"
            f"• Gênero: {gender} ({face['gender']['confidence']:.1f}% de confiança)\n"
            f"• Emoção predominante: {emotion} ({face['emotion']['confidence']:.1f}%)\n"
        )
        messages.append(message)
    
    return "\n\n".join(messages)

def send_notification(email, message, request_id):
    subject = f"📷 Resultado da Análise de Idade - {request_id}"
    
    try:
        # ✅ ARN CORRIGIDO (sua região e conta)
        response = sns.publish(
            TopicArn='arn:aws:sns:us-east-2:626064810617:age-estimation-system-dev-notifications',
            Message=message,
            Subject=subject,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                }
            }
        )
        print(f"✅ SNS response: {response['MessageId']}")
        
    except Exception as e:
        print(f"❌ Erro no SNS: {str(e)}")
        raise