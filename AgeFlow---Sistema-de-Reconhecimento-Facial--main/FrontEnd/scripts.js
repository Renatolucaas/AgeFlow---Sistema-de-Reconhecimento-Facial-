class AgeEstimationApp {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api/analyze';
        this.currentImage = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadHistory();
    }

    setupEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleImageSelect(files[0]);
            }
        });

        // File input
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleImageSelect(e.target.files[0]);
            }
        });

        // Enter key no email
        document.getElementById('userEmail').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processImage();
            }
        });
    }

    handleImageSelect(file) {
        if (!file.type.match('image.*')) {
            alert('Por favor, selecione um arquivo de imagem válido.');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert('A imagem deve ter menos de 5MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.currentImage = {
                file: file,
                dataUrl: e.target.result
            };
            this.showPreview();
        };
        reader.readAsDataURL(file);
    }

    showPreview() {
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('previewSection').style.display = 'block';
        document.getElementById('imagePreview').src = this.currentImage.dataUrl;
    }

    cancelUpload() {
        document.getElementById('previewSection').style.display = 'none';
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('imageInput').value = '';
        this.currentImage = null;
    }

    async processImage() {
        const email = document.getElementById('userEmail').value || 'anonymous@example.com';
        
        if (!this.currentImage) {
            alert('Por favor, selecione uma imagem primeiro.');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: this.currentImage.dataUrl,
                    email: email
                })
            });

            // Verifica se a resposta HTTP é OK
            if (!response.ok) {
                throw new Error(`Erro do servidor: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // CORREÇÃO: Verifica se requestId existe
                const requestId = data.results?.requestId || `req_${Date.now()}`;
                this.showSuccess(requestId);
                this.addToHistory(requestId, email);
                
                // Mostrar resultados reais da AWS Rekognition
                if (data.results) {
                    this.displayResults(data.results);
                }
            } else {
                // CORREÇÃO: Mensagem de erro mais segura
                const errorMsg = data.error || 'Erro desconhecido no servidor';
                this.showError(errorMsg);
            }
        } catch (error) {
            // CORREÇÃO: Mensagem de erro mais clara
            console.error('Erro completo:', error);
            this.showError('Erro de conexão com o servidor. Verifique se o backend está rodando.');
        }
    }

    showLoading() {
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsContent').innerHTML = '';
        document.getElementById('loading').style.display = 'block';
    }

    showSuccess(requestId) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('resultsContent').innerHTML = `
            <div class="success-message">
                <h4>✅ Imagem enviada com sucesso!</h4>
                <p>ID do processamento: ${requestId}</p>
                <p>Os resultados serão enviados para seu email em instantes.</p>
            </div>
        `;
    }

    showError(error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('resultsContent').innerHTML = `
            <div class="error-message">
                <h4>❌ Erro no processamento</h4>
                <p>${error}</p>
            </div>
        `;
    }

    displayResults(results) {
        let html = `<h4>🎯 Análise Concluída - ${results.facesDetected} face(s) detectada(s)</h4>`;
        
        if (results.facesDetected === 0) {
            html += `
                <div class="face-result">
                    <h4>❌ Nenhuma face detectada</h4>
                    <p>Tente com uma imagem mais clara ou com rostos mais visíveis.</p>
                </div>
            `;
        } else {
            results.faces.forEach((face, index) => {
                html += `
                    <div class="face-result">
                        <h4>👤 Face ${index + 1}</h4>
                        <div class="result-grid">
                            <div class="result-item">
                                <div class="result-value">${face.ageRange.estimated} anos</div>
                                <div class="result-label">Idade Estimada</div>
                                <div class="result-sub">Faixa: ${face.ageRange.low}-${face.ageRange.high}</div>
                            </div>
                            <div class="result-item">
                                <div class="result-value">${face.gender.value}</div>
                                <div class="result-label">Gênero</div>
                                <div class="result-sub">${face.gender.confidence.toFixed(1)}% confiança</div>
                            </div>
                            <div class="result-item">
                                <div class="result-value">${this.translateEmotion(face.emotion.type)}</div>
                                <div class="result-label">Emoção</div>
                                <div class="result-sub">${face.emotion.confidence.toFixed(1)}% confiança</div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        document.getElementById('resultsContent').innerHTML = html;
    }

    translateEmotion(emotion) {
        const emotions = {
            'HAPPY': '😊 Feliz',
            'SAD': '😢 Triste',
            'ANGRY': '😠 Bravo',
            'CONFUSED': '😕 Confuso',
            'DISGUSTED': '🤢 Enojado',
            'SURPRISED': '😮 Surpreso',
            'CALM': '😌 Calmo',
            'FEAR': '😨 Com medo'
        };
        return emotions[emotion] || emotion;
    }

    addToHistory(requestId, email) {
        const history = this.getHistory();
        history.unshift({
            requestId: requestId,
            email: email,
            timestamp: new Date().toISOString(),
            faces: 1 // Em produção viria do backend
        });
        
        // Manter apenas últimos 10 itens
        if (history.length > 10) {
            history.pop();
        }
        
        localStorage.setItem('ageEstimationHistory', JSON.stringify(history));
        this.loadHistory();
    }

    getHistory() {
        return JSON.parse(localStorage.getItem('ageEstimationHistory') || '[]');
    }

    loadHistory() {
        const history = this.getHistory();
        const historyList = document.getElementById('historyList');
        
        if (history.length === 0) {
            historyList.innerHTML = '<p>Nenhuma análise realizada ainda.</p>';
            return;
        }
        
        historyList.innerHTML = history.map(item => `
            <div class="history-item">
                <strong>ID:</strong> ${item.requestId.substring(0, 8)}...<br>
                <strong>Email:</strong> ${item.email}<br>
                <strong>Data:</strong> ${new Date(item.timestamp).toLocaleString()}<br>
                <strong>Faces:</strong> ${item.faces}
            </div>
        `).join('');
    }
}

// Inicializar aplicação
document.addEventListener('DOMContentLoaded', () => {
    // Definir a instância do aplicativo globalmente para que os manipuladores de clique no HTML possam acessá-lo.
    window.app = new AgeEstimationApp();
});