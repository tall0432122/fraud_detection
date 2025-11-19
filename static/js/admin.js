// Admin-specific JavaScript
class AdminDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initAdminCharts();
        this.setupAdminEvents();
        this.loadAdminData();
        this.setupRealTimeMonitoring();
    }

    initAdminCharts() {
        this.initUserActivityChart();
        this.initFraudTrendChart();
        this.initSystemMetricsChart();
    }

    initUserActivityChart() {
        const ctx = document.getElementById('userActivityChart');
        if (!ctx) return;

        this.charts.userActivity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'User Registrations',
                    data: [12, 19, 8, 15, 12, 5, 9],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)'
                }, {
                    label: 'Active Users',
                    data: [45, 42, 48, 52, 49, 38, 44],
                    backgroundColor: 'rgba(40, 167, 69, 0.8)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initFraudTrendChart() {
        const ctx = document.getElementById('fraudTrendChart');
        if (!ctx) return;

        this.charts.fraudTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                datasets: [{
                    label: 'Fraud Attempts',
                    data: Array.from({length: 24}, () => Math.floor(Math.random() * 10)),
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initSystemMetricsChart() {
        const ctx = document.getElementById('systemMetricsChart');
        if (!ctx) return;

        this.charts.systemMetrics = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['CPU Usage', 'Memory Usage', 'Disk Usage', 'Network'],
                datasets: [{
                    data: [45, 35, 60, 25],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            }
        });
    }

    setupAdminEvents() {
        this.setupUserManagement();
        this.setupModelManagement();
        this.setupAlertSystem();
        this.setupSystemControls();
    }

    setupUserManagement() {
        // Gestion de la recherche d'utilisateurs
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', this.debounce(this.searchUsers.bind(this), 300));
        }

        // Gestion des actions utilisateur
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-user-action')) {
                this.handleUserAction(e.target);
            }
        });
    }

    setupModelManagement() {
        // Gestion de l'entraînement des modèles
        const trainModelBtn = document.getElementById('trainModelBtn');
        if (trainModelBtn) {
            trainModelBtn.addEventListener('click', this.trainModel.bind(this));
        }

        // Gestion de l'évaluation des modèles
        const evaluateModelBtn = document.getElementById('evaluateModelBtn');
        if (evaluateModelBtn) {
            evaluateModelBtn.addEventListener('click', this.evaluateModel.bind(this));
        }
    }

    setupAlertSystem() {
        // Configuration des alertes
        const alertConfigForm = document.getElementById('alertConfigForm');
        if (alertConfigForm) {
            alertConfigForm.addEventListener('submit', this.saveAlertConfig.bind(this));
        }

        // Test des alertes
        const testAlertBtn = document.getElementById('testAlertBtn');
        if (testAlertBtn) {
            testAlertBtn.addEventListener('click', this.sendTestAlert.bind(this));
        }
    }

    setupSystemControls() {
        // Sauvegarde du système
        const backupBtn = document.getElementById('backupBtn');
        if (backupBtn) {
            backupBtn.addEventListener('click', this.createBackup.bind(this));
        }

        // Nettoyage des données
        const cleanupBtn = document.getElementById('cleanupBtn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', this.cleanupData.bind(this));
        }
    }

    async searchUsers(query) {
        try {
            const response = await fetch(`/api/admin/users/search?q=${encodeURIComponent(query)}`);
            const users = await response.json();
            this.displayUserSearchResults(users);
        } catch (error) {
            console.error('Error searching users:', error);
        }
    }

    displayUserSearchResults(users) {
        const resultsContainer = document.getElementById('userSearchResults');
        if (!resultsContainer) return;

        if (users.length === 0) {
            resultsContainer.innerHTML = '<div class="text-muted">No users found</div>';
            return;
        }

        const html = users.map(user => `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${user.username}</h6>
                        <small class="text-muted">${user.email}</small>
                    </div>
                    <div>
                        <span class="badge bg-${user.is_active ? 'success' : 'secondary'} me-2">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button class="btn btn-sm btn-outline-primary btn-user-action" 
                                data-user-id="${user.id}" data-action="edit">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        resultsContainer.innerHTML = html;
    }

    async handleUserAction(button) {
        const userId = button.dataset.userId;
        const action = button.dataset.action;

        try {
            let response;
            
            switch (action) {
                case 'edit':
                    this.editUser(userId);
                    break;
                case 'activate':
                    response = await fetch(`/api/admin/users/${userId}/activate`, { method: 'POST' });
                    break;
                case 'deactivate':
                    response = await fetch(`/api/admin/users/${userId}/deactivate`, { method: 'POST' });
                    break;
                case 'delete':
                    if (confirm('Are you sure you want to delete this user?')) {
                        response = await fetch(`/api/admin/users/${userId}`, { method: 'DELETE' });
                    }
                    break;
            }

            if (response && response.ok) {
                this.showAdminAlert('User action completed successfully', 'success');
                this.loadAdminData();
            }
        } catch (error) {
            console.error('Error performing user action:', error);
            this.showAdminAlert('Error performing user action', 'danger');
        }
    }

    async trainModel() {
        const button = document.getElementById('trainModelBtn');
        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';
        button.disabled = true;

        try {
            const response = await fetch('/api/admin/models/train', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showAdminAlert('Model training started successfully', 'success');
                this.monitorTrainingProgress();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error training model:', error);
            this.showAdminAlert('Error training model: ' + error.message, 'danger');
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async monitorTrainingProgress() {
        const progressBar = document.getElementById('trainingProgress');
        if (!progressBar) return;

        progressBar.style.display = 'block';
        
        const checkProgress = async () => {
            try {
                const response = await fetch('/api/admin/models/training-progress');
                const progress = await response.json();

                progressBar.querySelector('.progress-bar').style.width = `${progress.percent}%`;
                progressBar.querySelector('.progress-bar').textContent = `${progress.percent}%`;

                if (progress.status === 'completed') {
                    this.showAdminAlert('Model training completed successfully', 'success');
                    progressBar.style.display = 'none';
                    this.loadAdminData();
                } else if (progress.status === 'failed') {
                    this.showAdminAlert('Model training failed', 'danger');
                    progressBar.style.display = 'none';
                } else {
                    setTimeout(checkProgress, 1000);
                }
            } catch (error) {
                console.error('Error checking training progress:', error);
                progressBar.style.display = 'none';
            }
        };

        checkProgress();
    }

    async evaluateModel() {
        try {
            const response = await fetch('/api/admin/models/evaluate', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showAdminAlert('Model evaluation completed', 'success');
                this.displayModelMetrics(result.metrics);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error evaluating model:', error);
            this.showAdminAlert('Error evaluating model', 'danger');
        }
    }

    displayModelMetrics(metrics) {
        const metricsContainer = document.getElementById('modelMetrics');
        if (!metricsContainer) return;

        const html = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>${(metrics.accuracy * 100).toFixed(2)}%</h3>
                            <p class="text-muted">Accuracy</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>${(metrics.precision * 100).toFixed(2)}%</h3>
                            <p class="text-muted">Precision</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>${(metrics.recall * 100).toFixed(2)}%</h3>
                            <p class="text-muted">Recall</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3>${(metrics.f1_score * 100).toFixed(2)}%</h3>
                            <p class="text-muted">F1 Score</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        metricsContainer.innerHTML = html;
    }

    async saveAlertConfig(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const config = Object.fromEntries(formData);

        try {
            const response = await fetch('/api/admin/alerts/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                this.showAdminAlert('Alert configuration saved successfully', 'success');
            } else {
                throw new Error('Failed to save alert configuration');
            }
        } catch (error) {
            console.error('Error saving alert config:', error);
            this.showAdminAlert('Error saving alert configuration', 'danger');
        }
    }

    async sendTestAlert() {
        try {
            const response = await fetch('/api/admin/alerts/test', { method: 'POST' });
            
            if (response.ok) {
                this.showAdminAlert('Test alert sent successfully', 'success');
            } else {
                throw new Error('Failed to send test alert');
            }
        } catch (error) {
            console.error('Error sending test alert:', error);
            this.showAdminAlert('Error sending test alert', 'danger');
        }
    }

    async createBackup() {
        const button = document.getElementById('backupBtn');
        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Backing up...';
        button.disabled = true;

        try {
            const response = await fetch('/api/admin/system/backup', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showAdminAlert('Backup created successfully', 'success');
                
                // Télécharger le fichier de sauvegarde
                if (result.download_url) {
                    window.location.href = result.download_url;
                }
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error creating backup:', error);
            this.showAdminAlert('Error creating backup', 'danger');
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async cleanupData() {
        if (!confirm('Are you sure you want to cleanup old data? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/admin/system/cleanup', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showAdminAlert(`Cleanup completed. Freed ${result.freed_space} of space.`, 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error during cleanup:', error);
            this.showAdminAlert('Error during cleanup', 'danger');
        }
    }

    setupRealTimeMonitoring() {
        // Surveillance en temps réel des métriques système
        this.monitorSystemHealth();
        
        // Actualisation automatique des données
        setInterval(() => {
            this.loadAdminData();
        }, 60000); // Toutes les minutes
    }

    async monitorSystemHealth() {
        try {
            const response = await fetch('/api/admin/system/health');
            const health = await response.json();
            
            this.updateHealthIndicators(health);
        } catch (error) {
            console.error('Error monitoring system health:', error);
        }
    }

    updateHealthIndicators(health) {
        const indicators = {
            'databaseHealth': health.database,
            'modelHealth': health.model,
            'apiHealth': health.api,
            'storageHealth': health.storage
        };

        Object.keys(indicators).forEach(indicatorId => {
            const element = document.getElementById(indicatorId);
            if (element) {
                const status = indicators[indicatorId];
                element.className = `health-status health-${status}`;
                element.title = status.charAt(0).toUpperCase() + status.slice(1);
            }
        });
    }

    async loadAdminData() {
        await this.loadUserStatistics();
        await this.loadSystemMetrics();
        await this.loadRecentActivity();
    }

    async loadUserStatistics() {
        try {
            const response = await fetch('/api/admin/stats/users');
            const stats = await response.json();
            this.updateUserStatistics(stats);
        } catch (error) {
            console.error('Error loading user statistics:', error);
        }
    }

    updateUserStatistics(stats) {
        const elements = {
            'totalUsers': stats.total_users,
            'activeUsers': stats.active_users,
            'newUsersToday': stats.new_users_today,
            'avgPredictionsPerUser': stats.avg_predictions_per_user?.toFixed(1) || '0'
        };

        Object.keys(elements).forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = elements[elementId];
            }
        });
    }

    async loadSystemMetrics() {
        try {
            const response = await fetch('/api/admin/stats/system');
            const metrics = await response.json();
            this.updateSystemMetrics(metrics);
        } catch (error) {
            console.error('Error loading system metrics:', error);
        }
    }

    updateSystemMetrics(metrics) {
        // Mettre à jour les métriques système dans l'UI
        console.log('System metrics:', metrics);
    }

    async loadRecentActivity() {
        try {
            const response = await fetch('/api/admin/activity/recent');
            const activity = await response.json();
            this.updateRecentActivity(activity);
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    updateRecentActivity(activity) {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        const html = activity.map(item => `
            <div class="log-entry">
                <small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small>
                <div>${item.message}</div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    showAdminAlert(message, type) {
        // Utiliser le système d'alerte global ou créer un spécifique admin
        if (window.FraudDetect && window.FraudDetect.showAlert) {
            window.FraudDetect.showAlert(message, type);
        } else {
            // Fallback pour les alertes admin
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.getElementById('adminAlerts') || document.body;
            container.appendChild(alertDiv);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialiser le dashboard admin
document.addEventListener('DOMContentLoaded', function() {
    window.adminDashboard = new AdminDashboard();
});

// Fonctions globales pour l'admin
function refreshDashboard() {
    if (window.adminDashboard) {
        window.adminDashboard.loadAdminData();
    }
}

function sendTestAlert() {
    if (window.adminDashboard) {
        window.adminDashboard.sendTestAlert();
    }
}

function generateSystemReport() {
    window.location.href = '/api/admin/reports/system';
}