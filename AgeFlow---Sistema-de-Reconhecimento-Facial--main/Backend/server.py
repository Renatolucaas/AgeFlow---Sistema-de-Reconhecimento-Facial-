from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Adiciona o diretório pai ao path para importar o simple_processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Backend.simple_processor import AgeEstimationProcessor
    print("✅ AgeEstimationProcessor importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar simple_processor: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Inicializa o processador
try:
    processor = AgeEstimationProcessor()
    print("✅ AgeEstimationProcessor inicializado!")
except Exception as e:
    print(f"❌ Erro ao inicializar processador: {e}")
    sys.exit(1)

def send_email_results(email, results):
    """Envia os resultados da análise por email"""
    try:
        # CONFIGURAÇÃO GMAIL COM SUA SENHA DE APP
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "sistemaweb2025.2ucl@gmail.com"
        password = "sbhn pdto sjjv wlio"  # ⬅️ SUA SENHA DE APP IMPLEMENTADA

        # Criar mensagem
        message = MIMEMultipart("alternative")
        message["Subject"] = "📊 Resultados da Análise Facial"
        message["From"] = sender_email
        message["To"] = email

        # Conteúdo do email
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #3498db; text-align: center;">📊 Resultados da Análise Facial</h2>
                <p><strong>Faces detectadas:</strong> {results['facesDetected']}</p>
                <p><strong>ID da análise:</strong> {results['requestId']}</p>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Detalhes das faces:</h3>
                {"".join([f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 8px; background: #f8f9fa;">
                  <h4 style="color: #e74c3c; margin-top: 0;">👤 Face {i+1}</h4>
                  <p><strong>Idade:</strong> {face['ageRange']['estimated']} anos (faixa: {face['ageRange']['low']}-{face['ageRange']['high']})</p>
                  <p><strong>Gênero:</strong> {face['gender']['value']} ({face['gender']['confidence']:.1f}% confiança)</p>
                  <p><strong>Emoção:</strong> {face['emotion']['type']} ({face['emotion']['confidence']:.1f}% confiança)</p>
                </div>
                """ for i, face in enumerate(results['faces'])])}
                
                <div style="margin-top: 20px; padding: 15px; background: #e8f4fd; border-radius: 5px; text-align: center;">
                    <p style="margin: 0; color: #2c3e50;">Obrigado por usar nosso serviço de análise facial! 🎉</p>
                </div>
            </div>
          </body>
        </html>
        """

        message.attach(MIMEText(html, "html"))

        # Enviar email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message.as_string())
        
        print(f"✅ Email enviado com sucesso para: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email para {email}: {e}")
        return False

@app.route('/')
def serve_frontend():
    """Serve a interface HTML principal"""
    try:
        # Caminho correto para o index.html na pasta frontend
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(project_root, 'frontend', 'index.html')
        
        print(f"🔍 Procurando HTML em: {html_path}")
        
        if os.path.exists(html_path):
            print("✅ HTML encontrado! Servindo interface...")
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Debug: mostra o que existe
            frontend_dir = os.path.join(project_root, 'frontend')
            if os.path.exists(frontend_dir):
                files = os.listdir(frontend_dir)
                print(f"📁 Arquivos em frontend/: {files}")
            else:
                print("❌ Pasta frontend/ não existe!")
                
            error_html = f"""
            <html>
                <head><title>Erro - Arquivo não encontrado</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; background: #f8f9fa;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h1 style="color: #e74c3c;">❌ Arquivo index.html não encontrado</h1>
                        <h3>🔍 Procurando em:</h3>
                        <code style="background: #f1f1f1; padding: 10px; display: block; border-radius: 5px;">{html_path}</code>
                        
                        <h3>📁 Estrutura do projeto:</h3>
                        <ul style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            """
            # Lista arquivos do projeto para debug
            for item in os.listdir(project_root):
                item_path = os.path.join(project_root, item)
                if os.path.isdir(item_path):
                    error_html += f'<li>📁 {item}/</li>'
                else:
                    error_html += f'<li>📄 {item}</li>'
            
            error_html += """
                        </ul>
                        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
                            <strong>💡 Solução:</strong> Verifique se o arquivo index.html está na pasta frontend/
                        </div>
                    </div>
                </body>
            </html>
            """
            return error_html, 404
            
    except Exception as e:
        error_msg = f"Erro ao carregar interface: {str(e)}"
        print(f"❌ {error_msg}")
        return f"<h1>Erro</h1><p>{error_msg}</p>", 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos (CSS, JS) da pasta frontend"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, 'frontend', filename)

        if os.path.exists(file_path):
            # Determina o content type baseado na extensão
            if filename.endswith('.css'):
                mimetype = 'text/css'
            elif filename.endswith('.js'):
                mimetype = 'application/javascript'
            else:
                mimetype = 'text/plain'
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': mimetype}
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Endpoint para análise de imagem"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False, 
                'error': 'Nenhuma imagem fornecida'
            }), 400
        
        print("🖼️ Processando imagem recebida...")

        # Processa a imagem base64
        result = processor.process_base64_image(data['image'])
        
        if result['success']:
            print(f"✅ Análise concluída: {result['results']['facesDetected']} face(s) detectada(s)")
            
            # ENVIAR EMAIL SE FORNECIDO
            user_email = data.get('email', '')
            if user_email and user_email != 'anonymous@example.com':
                print(f"📧 Enviando resultados para: {user_email}")
                send_email_results(user_email, result['results'])
            else:
                print("ℹ️  Email não fornecido - pulando envio")
                
        else:
            print(f"❌ Erro na análise: {result['error']}")
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'Erro no servidor: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({
            'success': False, 
            'error': error_msg
        }), 500

@app.route('/api/health')
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    aws_connected = processor.check_credentials()
    return jsonify({
        'status': 'healthy',
        'service': 'Age Estimation API',
        'aws_connected': aws_connected,
        'message': '✅ Servidor funcionando perfeitamente!' if aws_connected else '❌ Problema com AWS'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO SERVIDOR DE ESTIMATIVA DE IDADE")
    print("=" * 60)

    # Verifica credenciais AWS
    print("📧 Verificando credenciais AWS...")
    if processor.check_credentials():
        print("✅ AWS configurada corretamente!")
        print("🌐 Servidor rodando em: http://localhost:5000")
        print("📷 Interface: http://localhost:5000")
        print("🔍 Endpoint de saúde: http://localhost:5000/api/health")
        print("📨 Suporte a email: ✅ ATIVADO")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Erro: Credenciais AWS não configuradas")
        print("💡 Execute: aws configure")