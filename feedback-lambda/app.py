import json
import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            request_id = message['requestId']
            user_email = message['userEmail']
            results = message['results']
            
            # Gerar mensagem de feedback
            feedback_message = generate_feedback_message(results)

            
            # Enviar notificação via SNS
            send_notification(user_email, feedback_message, request_id)
            
            print(f"Feedback enviado para {user_email}")
            
        except Exception as e:
            print(f"Erro no envio de feedback: {str(e)}")
            continue

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
    
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:age-estimation-system-dev-notifications',
        Message=message,
        Subject=subject,
        MessageAttributes={
            'email': {
                'DataType': 'String',
                'StringValue': email
            }
        }
    )