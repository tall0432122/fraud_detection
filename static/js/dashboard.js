// Dashboard-specific JavaScript
class Dashboard {
    constructor() {
        this.charts = {};
        this.statsInterval = null;
        this.init();
    }

    init() {
        this.initCharts();
        this.initRealTimeUpdates();
        this.setupDashboardEvents();
        this.loadInitialData();
    }

    initCharts() {
        // Chart.js initialization for prediction distribution
        this.initPredictionChart();
        
        // Chart.js initialization for detection trends
        this.initTrendChart();
        
        // Chart.js initialization for confidence distribution
        this.initConfidenceChart();
    }

    initPredictionChart() {
        const ctx = document.getElementById('predictionPieChart');
        if (!ctx) return;

        this.charts.prediction = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Safe Transactions', 'Fraud Detected'],
                datasets: [{
                    data: [70, 30], // Données initiales
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    initTrendChart() {
        const ctx = document.getElementById('detectionChart');
        if (!ctx) return;

        const now = new Date();
        const labels = [];
        for (let i = 6; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        }

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Fraud Detected',
                    data: [2, 5, 3, 7, 4, 6, 3],
                    borderColor: 'rgba(220, 53, 69, 1)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Total Transactions',
                    data: [45, 52, 48, 55, 50, 53, 49],
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Transactions'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }

    initConfidenceChart() {
        const ctx = document.getElementById('confidenceChart');
        if (!ctx) return;

        this.charts.confidence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                datasets: [{
                    label: 'Confidence Distribution',
                    data: [5, 12, 8, 15, 10],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Predictions'
                        }
                    }
                }
            }
        });
    }

    initRealTimeUpdates() {
        // Mettre à jour les stats toutes les 30 secondes
        this.statsInterval = setInterval(() => {
            this.updateDashboardStats();
        }, 30000);

        // WebSocket pour les mises à jour en temps réel
        this.initWebSocket();
    }

    initWebSocket() {
        // Implémentation WebSocket pour les alertes en temps réel
        // À adapter selon votre configuration serveur
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealTimeUpdate(data);
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket connection closed');
                // Tentative de reconnexion après 5 secondes
                setTimeout(() => this.initWebSocket(), 5000);
            };
            
        } catch (error) {
            console.log('WebSocket not available, using polling');
        }
    }

    handleRealTimeUpdate(data) {
        if (data.type === 'new_prediction') {
            this.addNewPrediction(data.prediction);
            this.updateCharts(data.prediction);
            this.showRealTimeAlert(data.prediction);
        } else if (data.type === 'stats_update') {
            this.updateStatsDisplay(data.stats);
        }
    }

    addNewPrediction(prediction) {
        const activityList = document.getElementById('recentActivityList');
        if (!activityList) return;

        const activityItem = this.createActivityItem(prediction);
        activityList.insertBefore(activityItem, activityList.firstChild);

        // Garder seulement les 10 dernières activités
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    createActivityItem(prediction) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const iconClass = prediction.prediction === 'Fraude' ? 
            'fas fa-exclamation-triangle text-danger' : 
            'fas fa-check-circle text-success';
        
        const time = new Date(prediction.created_at).toLocaleTimeString();
        
        item.innerHTML = `
            <div class="activity-icon">
                <i class="${iconClass}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-text">
                    ${prediction.prediction === 'Fraude' ? 'Fraud detected' : 'Safe transaction'} 
                    with ${(prediction.confidence * 100).toFixed(1)}% confidence
                </div>
                <div class="activity-time">${time}</div>
            </div>
        `;
        
        return item;
    }

    updateCharts(prediction) {
        // Mettre à jour les graphiques avec la nouvelle prédiction
        if (this.charts.prediction) {
            // Simuler la mise à jour du graphique circulaire
            const isFraud = prediction.prediction === 'Fraude';
            const fraudIndex = 1;
            const safeIndex = 0;
            
            this.charts.prediction.data.datasets[0].data[isFraud ? fraudIndex : safeIndex]++;
            this.charts.prediction.update();
        }

        if (this.charts.trend) {
            // Mettre à jour le graphique de tendance
            // Cette logique devrait être adaptée selon vos données réelles
            this.charts.trend.data.datasets[0].data[6]++;
            this.charts.trend.data.datasets[1].data[6]++;
            this.charts.trend.update();
        }
    }

    showRealTimeAlert(prediction) {
        if (prediction.prediction === 'Fraude' && prediction.confidence > 0.7) {
            const alertMessage = `🚨 High-confidence fraud detected! Confidence: ${(prediction.confidence * 100).toFixed(1)}%`;
            
            // Créer une notification toast
            this.showToastNotification(alertMessage, 'danger');
            
            // Jouer un son d'alerte (optionnel)
            this.playAlertSound();
        }
    }

    showToastNotification(message, type) {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-bell me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();
        
        // Nettoyer après la fermeture
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    playAlertSound() {
        // Jouer un son d'alerte simple
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.1);
        gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    setupDashboardEvents() {
        // Rafraîchir les statistiques manuellement
        const refreshBtn = document.getElementById('refreshStats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.updateDashboardStats();
                this.showAlert('Dashboard refreshed', 'info');
            });
        }

        // Gestionnaire pour les filtres de date
        const dateFilter = document.getElementById('dateFilter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.applyDateFilter(e.target.value);
            });
        }

        // Exporter les données du dashboard
        const exportBtn = document.getElementById('exportDashboard');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportDashboardData();
            });
        }
    }

    async updateDashboardStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            this.updateStatsDisplay(stats);
        } catch (error) {
            console.error('Error updating dashboard stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        // Mettre à jour les cartes de statistiques
        const elements = {
            'totalPredictions': stats.total,
            'fraudCases': stats.fraud,
            'safeTransactions': stats.non_fraud,
            'fraudRate': stats.avg_confidence ? `${((stats.fraud / stats.total) * 100).toFixed(1)}%` : '0%'
        };

        Object.keys(elements).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = elements[key];
            }
        });
    }

    async loadInitialData() {
        await this.updateDashboardStats();
        this.updateChartsFromServer();
    }

    async updateChartsFromServer() {
        try {
            const response = await fetch('/api/chart-data');
            const chartData = await response.json();
            
            // Mettre à jour les graphiques avec les données du serveur
            if (this.charts.prediction && chartData.pie) {
                this.charts.prediction.data.datasets[0].data = chartData.pie.values;
                this.charts.prediction.update();
            }
            
            if (this.charts.trend && chartData.trend) {
                this.charts.trend.data.labels = chartData.trend.labels;
                this.charts.trend.data.datasets[0].data = chartData.trend.fraudData;
                this.charts.trend.data.datasets[1].data = chartData.trend.totalData;
                this.charts.trend.update();
            }
            
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    applyDateFilter(range) {
        // Appliquer un filtre de date aux données du dashboard
        console.log('Applying date filter:', range);
        // Implémentation spécifique selon vos besoins
    }

    exportDashboardData() {
        // Exporter les données du dashboard
        const data = {
            timestamp: new Date().toISOString(),
            charts: this.charts
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fraud-dashboard-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showAlert('Dashboard data exported successfully', 'success');
    }

    showAlert(message, type) {
        if (window.FraudDetect && window.FraudDetect.showAlert) {
            window.FraudDetect.showAlert(message, type);
        } else {
            alert(message);
        }
    }

    destroy() {
        // Nettoyer les ressources
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
        }
        
        if (this.socket) {
            this.socket.close();
        }
        
        // Détruire les graphiques
        Object.values(this.charts).forEach(chart => {
            chart.destroy();
        });
    }
}

// Initialiser le dashboard lorsque la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    window.fraudDashboard = new Dashboard();
});

// Exporter pour une utilisation globale
window.Dashboard = Dashboard;