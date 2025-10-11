from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

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

@app.route('/')
def serve_frontend():
    """Serve a interface HTML principal"""