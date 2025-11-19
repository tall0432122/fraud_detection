// Configuration globale
const CONFIG = {
    API_BASE_URL: '/api',
    REFRESH_INTERVAL: 30000,
    MAX_FILE_SIZE: 16 * 1024 * 1024 // 16MB
};

// Initialisation lorsque le document est prêt
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupLanguageSelector();
});

function initializeApp() {
    // Initialiser les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialiser les popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Vérifier la connexion Internet
    checkInternetConnection();
}

function setupEventListeners() {
    // Gestionnaire pour les formulaires de prédiction
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePredictionSubmit);
    }

    // Gestionnaire pour l'upload de fichiers batch
    const batchForm = document.getElementById('batchForm');
    if (batchForm) {
        batchForm.addEventListener('submit', handleBatchUpload);
    }

    // Gestionnaire pour le drag and drop
    setupDragAndDrop();

    // Gestionnaire pour les boutons de feedback
    setupFeedbackButtons();

    // Gestionnaire pour la génération de rapports
    setupReportGeneration();
}

function setupLanguageSelector() {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function(e) {
            const selectedLanguage = e.target.value;
            setLanguage(selectedLanguage);
        });
    }
}

function setLanguage(language) {
    fetch('/set_language/' + language, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error changing language:', error);
        showAlert('Error changing language', 'danger');
    });
}

async function handlePredictionSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const resultsSection = document.getElementById('predictionResults');
    const loadingSpinner = document.getElementById('predictionLoading');
    
    // Afficher le loading
    showLoading(loadingSpinner, submitButton);
    
    try {
        const formData = new FormData(form);
        const response = await fetch('/prediction', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newResults = doc.getElementById('predictionResults');
            
            if (newResults && resultsSection) {
                resultsSection.innerHTML = newResults.innerHTML;
                resultsSection.style.display = 'block';
                
                // Animer l'apparition des résultats
                animateResults(resultsSection);
                
                // Mettre à jour les statistiques du dashboard
                updateDashboardStats();
            }
        } else {
            throw new Error('Prediction failed');
        }
    } catch (error) {
        console.error('Prediction error:', error);
        showAlert('Error processing prediction', 'danger');
    } finally {
        hideLoading(loadingSpinner, submitButton);
    }
}

async function handleBatchUpload(e) {
    e.preventDefault();
    
    const form = e.target;
    const fileInput = document.getElementById('batchFile');
    const resultsDiv = document.getElementById('batchResults');
    const resultsTable = document.getElementById('resultsTable');
    
    if (!fileInput.files.length) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validation du fichier
    if (!validateFile(file)) {
        return;
    }
    
    showLoading(null, form.querySelector('button[type="submit"]'));
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/batch_prediction', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBatchResults(data.results, resultsTable);
            resultsDiv.style.display = 'block';
            showAlert('Batch analysis completed successfully', 'success');
        } else {
            throw new Error(data.error || 'Batch analysis failed');
        }
    } catch (error) {
        console.error('Batch upload error:', error);
        showAlert('Error processing batch file: ' + error.message, 'danger');
    } finally {
        hideLoading(null, form.querySelector('button[type="submit"]'));
    }
}

function validateFile(file) {
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showAlert('File size exceeds maximum limit (16MB)', 'danger');
        return false;
    }
    
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showAlert('Please upload a CSV file', 'warning');
        return false;
    }
    
    return true;
}

function displayBatchResults(results, container) {
    if (!container) return;
    
    let html = `
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Transaction ID</th>
                        <th>Prediction</th>
                        <th>Confidence</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    results.forEach(result => {
        const riskLevel = getRiskLevel(result.confidence, result.prediction);
        const riskClass = getRiskClass(riskLevel);
        
        html += `
            <tr>
                <td>${result.transaction_id}</td>
                <td>
                    <span class="badge bg-${result.prediction === 'Fraude' ? 'danger' : 'success'}">
                        ${result.prediction}
                    </span>
                </td>
                <td>${(result.confidence * 100).toFixed(2)}%</td>
                <td>
                    <span class="badge bg-${riskClass}">
                        <span class="risk-indicator risk-${riskLevel}"></span>
                        ${riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)}
                    </span>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <div class="mt-3">
            <strong>Summary:</strong> ${results.length} transactions analyzed
        </div>
    `;
    
    container.innerHTML = html;
}

function getRiskLevel(confidence, prediction) {
    if (prediction === 'Fraude') {
        if (confidence > 0.8) return 'high';
        if (confidence > 0.6) return 'medium';
        return 'low';
    }
    return 'low';
}

function getRiskClass(riskLevel) {
    const riskClasses = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'success'
    };
    return riskClasses[riskLevel] || 'secondary';
}

function setupDragAndDrop() {
    const dropArea = document.getElementById('batchUploadArea');
    
    if (!dropArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('dragover');
    }
    
    function unhighlight() {
        dropArea.classList.remove('dragover');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.getElementById('batchFile');
        
        if (files.length) {
            fileInput.files = files;
            
            // Déclencher l'événement change pour mettre à jour l'UI
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
}

function setupFeedbackButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('feedback-btn')) {
            const predictionId = e.target.dataset.predictionId;
            const isCorrect = e.target.dataset.isCorrect === 'true';
            const actualLabel = e.target.dataset.actualLabel;
            
            provideFeedback(predictionId, isCorrect, actualLabel);
        }
    });
}

async function provideFeedback(predictionId, isCorrect, actualLabel) {
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prediction_id: predictionId,
                is_correct: isCorrect,
                actual_label: parseInt(actualLabel)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Feedback submitted successfully', 'success');
            
            // Masquer les boutons de feedback
            const feedbackSection = document.querySelector(`[data-prediction-id="${predictionId}"]`).closest('.feedback-section');
            if (feedbackSection) {
                feedbackSection.innerHTML = '<p class="text-success"><i class="fas fa-check-circle"></i> Thank you for your feedback!</p>';
            }
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Feedback error:', error);
        showAlert('Error submitting feedback', 'danger');
    }
}

function setupReportGeneration() {
    const reportButtons = document.querySelectorAll('.generate-report');
    
    reportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reportType = this.dataset.reportType;
            generateReport(reportType);
        });
    });
}

function generateReport(reportType) {
    const button = document.querySelector(`[data-report-type="${reportType}"]`);
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    button.disabled = true;
    
    window.location.href = `/generate_report/${reportType}`;
    
    // Réactiver le bouton après un délai
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

function showLoading(loadingElement, buttonElement) {
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
    if (buttonElement) {
        buttonElement.disabled = true;
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    }
}

function hideLoading(loadingElement, buttonElement) {
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
    if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.innerHTML = '<i class="fas fa-search"></i> Analyze Transaction';
    }
}

function animateResults(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    requestAnimationFrame(() => {
        element.style.transition = 'all 0.5s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    });
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

function checkInternetConnection() {
    if (!navigator.onLine) {
        showAlert('You are currently offline. Some features may not work properly.', 'warning');
    }
    
    window.addEventListener('online', () => {
        showAlert('Internet connection restored', 'success');
    });
    
    window.addEventListener('offline', () => {
        showAlert('Internet connection lost', 'warning');
    });
}

// Fonctions utilitaires
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export pour utilisation globale
window.FraudDetect = {
    showAlert,
    setLanguage,
    formatCurrency,
    formatDate
};