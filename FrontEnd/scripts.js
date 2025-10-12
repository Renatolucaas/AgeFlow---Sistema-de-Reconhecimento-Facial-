class AgeEstimationApp {
    constructor() {
        this.apiUrl = 'https://your-api-id.execute-api.region.amazonaws.com/dev/upload';
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

            const data = await response.json();

            if (data.success) {
                this.showSuccess(data.requestId);
                this.addToHistory(data.requestId, email);
                
                // Simular recebimento de resultados (em produção seria via WebSocket ou polling)
                setTimeout(() => {
                    this.simulateResults(data.requestId);
                }, 3000);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Erro de conexão: ' + error.message);
        }
    }



    }
    
