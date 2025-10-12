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
}