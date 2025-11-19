// Charts.js configuration and utilities
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
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
                    mode: 'index',
                    intersect: false
                }
            }
        };
    }

    // Initialize all charts on the page
    initCharts() {
        this.initFraudTrendChart();
        this.initPredictionDistributionChart();
        this.initConfidenceDistributionChart();
        this.initGeographicDistributionChart();
        this.initTimeAnalysisChart();
        this.initModelPerformanceChart();
    }

    // Fraud trend over time
    initFraudTrendChart() {
        const ctx = document.getElementById('fraudTrendChart');
        if (!ctx) return;

        const data = {
            labels: this.generateDateLabels(30),
            datasets: [{
                label: 'Fraud Cases',
                data: this.generateRandomData(30, 5, 20),
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Total Transactions',
                data: this.generateRandomData(30, 100, 200),
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        const options = {
            ...this.defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Transactions'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        };

        this.charts.set('fraudTrend', new Chart(ctx, {
            type: 'line',
            data: data,
            options: options
        }));
    }

    // Prediction distribution pie chart
    initPredictionDistributionChart() {
        const ctx = document.getElementById('predictionDistributionChart');
        if (!ctx) return;

        const data = {
            labels: ['Safe Transactions', 'Fraud Detected', 'Suspicious', 'Under Review'],
            datasets: [{
                data: [65, 15, 12, 8],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(108, 117, 125, 0.8)'
                ],
                borderColor: [
                    'rgb(40, 167, 69)',
                    'rgb(220, 53, 69)',
                    'rgb(255, 193, 7)',
                    'rgb(108, 117, 125)'
                ],
                borderWidth: 2
            }]
        };

        const options = {
            ...this.defaultOptions,
            plugins: {
                ...this.defaultOptions.plugins,
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
        };

        this.charts.set('predictionDistribution', new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: options
        }));
    }

    // Confidence level distribution
    initConfidenceDistributionChart() {
        const ctx = document.getElementById('confidenceDistributionChart');
        if (!ctx) return;

        const data = {
            labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
            datasets: [{
                label: 'Number of Predictions',
                data: [5, 12, 25, 35, 23],
                backgroundColor: 'rgba(52, 152, 219, 0.8)',
                borderColor: 'rgb(52, 152, 219)',
                borderWidth: 1
            }]
        };

        const options = {
            ...this.defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Predictions'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Confidence Level'
                    }
                }
            }
        };

        this.charts.set('confidenceDistribution', new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
        }));
    }

    // Geographic distribution of fraud
    initGeographicDistributionChart() {
        const ctx = document.getElementById('geographicDistributionChart');
        if (!ctx) return;

        const data = {
            labels: ['North America', 'Europe', 'Asia', 'Africa', 'South America', 'Oceania'],
            datasets: [{
                label: 'Fraud Cases',
                data: [45, 30, 15, 5, 3, 2],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ]
            }]
        };

        this.charts.set('geographicDistribution', new Chart(ctx, {
            type: 'polarArea',
            data: data,
            options: this.defaultOptions
        }));
    }

    // Time-based analysis
    initTimeAnalysisChart() {
        const ctx = document.getElementById('timeAnalysisChart');
        if (!ctx) return;

        const data = {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [{
                label: 'Fraud Attempts',
                data: [8, 5, 12, 25, 30, 20],
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };

        const options = {
            ...this.defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Fraud Attempts'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time of Day'
                    }
                }
            }
        };

        this.charts.set('timeAnalysis', new Chart(ctx, {
            type: 'line',
            data: data,
            options: options
        }));
    }

    // Model performance comparison
    initModelPerformanceChart() {
        const ctx = document.getElementById('modelPerformanceChart');
        if (!ctx) return;

        const data = {
            labels: ['Random Forest', 'Gradient Boosting', 'Logistic Regression', 'Neural Network', 'SVM'],
            datasets: [{
                label: 'Accuracy',
                data: [98.2, 97.5, 95.8, 96.3, 94.7],
                backgroundColor: 'rgba(40, 167, 69, 0.8)'
            }, {
                label: 'Precision',
                data: [96.8, 96.2, 94.5, 95.1, 93.2],
                backgroundColor: 'rgba(52, 152, 219, 0.8)'
            }, {
                label: 'Recall',
                data: [95.5, 94.8, 93.2, 93.9, 92.1],
                backgroundColor: 'rgba(255, 193, 7, 0.8)'
            }]
        };

        const options = {
            ...this.defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                }
            },
            plugins: {
                ...this.defaultOptions.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            }
        };

        this.charts.set('modelPerformance', new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
        }));
    }

    // Utility methods
    generateDateLabels(days) {
        const labels = [];
        const now = new Date();
        
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            }));
        }
        
        return labels;
    }

    generateRandomData(count, min, max) {
        return Array.from({ length: count }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    // Update chart data
    updateChart(chartName, newData) {
        const chart = this.charts.get(chartName);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    // Add new data point to a chart
    addDataPoint(chartName, label, dataPoint) {
        const chart = this.charts.get(chartName);
        if (chart) {
            chart.data.labels.push(label);
            chart.data.datasets.forEach((dataset, index) => {
                dataset.data.push(dataPoint[index]);
            });
            
            // Keep only last 50 data points
            if (chart.data.labels.length > 50) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => {
                    dataset.data.shift();
                });
            }
            
            chart.update();
        }
    }

    // Export chart as image
    exportChart(chartName, format = 'png') {
        const chart = this.charts.get(chartName);
        if (chart) {
            const link = document.createElement('a');
            link.download = `chart-${chartName}-${new Date().toISOString().split('T')[0]}.${format}`;
            link.href = chart.toBase64Image();
            link.click();
        }
    }

    // Destroy all charts
    destroyAll() {
        this.charts.forEach((chart, name) => {
            chart.destroy();
        });
        this.charts.clear();
    }

    // Get chart data as JSON
    getChartData(chartName) {
        const chart = this.charts.get(chartName);
        return chart ? chart.data : null;
    }

    // Apply theme to all charts
    applyTheme(theme) {
        const isDark = theme === 'dark';
        const textColor = isDark ? '#ffffff' : '#666666';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

        this.charts.forEach(chart => {
            chart.options.scales.x.ticks.color = textColor;
            chart.options.scales.y.ticks.color = textColor;
            chart.options.scales.x.grid.color = gridColor;
            chart.options.scales.y.grid.color = gridColor;
            chart.options.plugins.legend.labels.color = textColor;
            chart.update();
        });
    }
}

// Real-time chart updates
class RealTimeChartUpdater {
    constructor(chartManager) {
        this.chartManager = chartManager;
        this.updateInterval = null;
        this.isUpdating = false;
    }

    startRealTimeUpdates(interval = 5000) {
        this.stopRealTimeUpdates();
        
        this.updateInterval = setInterval(() => {
            this.updateChartsWithLiveData();
        }, interval);
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateChartsWithLiveData() {
        if (this.isUpdating) return;
        this.isUpdating = true;

        try {
            // Simulate API call to get live data
            const liveData = await this.fetchLiveData();
            
            // Update fraud trend chart
            const now = new Date();
            const timeLabel = now.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            this.chartManager.addDataPoint('fraudTrend', timeLabel, [
                Math.floor(Math.random() * 10) + 1,  // Fraud cases
                Math.floor(Math.random() * 50) + 50  // Total transactions
            ]);

        } catch (error) {
            console.error('Error updating charts with live data:', error);
        } finally {
            this.isUpdating = false;
        }
    }

    async fetchLiveData() {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    fraudCases: Math.floor(Math.random() * 10) + 1,
                    totalTransactions: Math.floor(Math.random() * 50) + 50,
                    confidenceLevels: this.generateRandomConfidenceLevels()
                });
            }, 1000);
        });
    }

    generateRandomConfidenceLevels() {
        return Array.from({ length: 5 }, () => Math.floor(Math.random() * 20) + 5);
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chartManager = new ChartManager();
    window.chartManager.initCharts();

    // Initialize real-time updates if on dashboard
    if (document.getElementById('fraudTrendChart')) {
        window.realTimeUpdater = new RealTimeChartUpdater(window.chartManager);
        window.realTimeUpdater.startRealTimeUpdates(10000); // Update every 10 seconds
    }
});

// Export for global access
window.ChartManager = ChartManager;
window.RealTimeChartUpdater = RealTimeChartUpdater;