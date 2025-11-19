// Translation management and language utilities
class TranslationManager {
    constructor() {
        this.currentLanguage = 'fr';
        this.translations = {};
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        try {
            // Load translations from server or local storage
            await this.loadTranslations();
            this.currentLanguage = this.getStoredLanguage() || 'fr';
            this.applyTranslations();
            this.initialized = true;
            
            console.log('Translation manager initialized with language:', this.currentLanguage);
        } catch (error) {
            console.error('Failed to initialize translation manager:', error);
        }
    }

    async loadTranslations() {
        // Try to load from localStorage first
        const cachedTranslations = localStorage.getItem('appTranslations');
        
        if (cachedTranslations) {
            this.translations = JSON.parse(cachedTranslations);
        } else {
            // Load from server
            try {
                const response = await fetch('/api/translations');
                this.translations = await response.json();
                localStorage.setItem('appTranslations', JSON.stringify(this.translations));
            } catch (error) {
                console.warn('Could not load translations from server, using defaults');
                this.translations = this.getDefaultTranslations();
            }
        }
    }

    getDefaultTranslations() {
        return {
            fr: {
                // Navigation
                "Welcome to FraudDetect": "Bienvenue sur FraudDetect",
                "Fraud Detection System": "Système de Détection de Fraude",
                "Dashboard": "Tableau de Bord",
                "Real-time Detection": "Détection en Temps Réel",
                "Analysis": "Analyse",
                "Reports": "Rapports",
                "Profile": "Profil",
                "Logout": "Déconnexion",
                "Login": "Connexion",
                "Register": "Inscription",
                
                // Dashboard
                "Total Predictions": "Total des Prédictions",
                "Fraud Cases": "Cas de Fraude",
                "Safe Transactions": "Transactions Sûres",
                "Fraud Rate": "Taux de Fraude",
                "Recent Activity": "Activité Récente",
                "High Risk": "Risque Élevé",
                "Medium Risk": "Risque Moyen",
                "Low Risk": "Risque Faible",
                
                // Prediction
                "Transaction Amount": "Montant de la Transaction",
                "Currency": "Devise",
                "Analyze Transaction": "Analyser la Transaction",
                "Detection Results": "Résultats de la Détection",
                "Fraud Detected": "Fraude Détectée",
                "No Fraud Detected": "Aucune Fraude Détectée",
                "Confidence Level": "Niveau de Confiance",
                
                // Common
                "Save": "Sauvegarder",
                "Cancel": "Annuler",
                "Delete": "Supprimer",
                "Edit": "Modifier",
                "View": "Voir",
                "Download": "Télécharger",
                "Upload": "Téléverser",
                "Search": "Rechercher",
                "Filter": "Filtrer",
                "Refresh": "Actualiser",
                
                // Messages
                "Operation completed successfully": "Opération terminée avec succès",
                "An error occurred": "Une erreur est survenue",
                "Loading...": "Chargement...",
                "No data available": "Aucune donnée disponible",
                
                // Time
                "Just now": "À l'instant",
                "minutes ago": "minutes",
                "hours ago": "heures",
                "days ago": "jours"
            },
            en: {
                // English translations (usually the source)
                "Welcome to FraudDetect": "Welcome to FraudDetect",
                "Fraud Detection System": "Fraud Detection System",
                "Dashboard": "Dashboard",
                "Real-time Detection": "Real-time Detection",
                "Analysis": "Analysis",
                "Reports": "Reports",
                "Profile": "Profile",
                "Logout": "Logout",
                "Login": "Login",
                "Register": "Register",
                
                // Keep all English keys the same
                "Total Predictions": "Total Predictions",
                "Fraud Cases": "Fraud Cases",
                "Safe Transactions": "Safe Transactions",
                "Fraud Rate": "Fraud Rate",
                "Recent Activity": "Recent Activity",
                "High Risk": "High Risk",
                "Medium Risk": "Medium Risk",
                "Low Risk": "Low Risk",
                
                "Transaction Amount": "Transaction Amount",
                "Currency": "Currency",
                "Analyze Transaction": "Analyze Transaction",
                "Detection Results": "Detection Results",
                "Fraud Detected": "Fraud Detected",
                "No Fraud Detected": "No Fraud Detected",
                "Confidence Level": "Confidence Level",
                
                "Save": "Save",
                "Cancel": "Cancel",
                "Delete": "Delete",
                "Edit": "Edit",
                "View": "View",
                "Download": "Download",
                "Upload": "Upload",
                "Search": "Search",
                "Filter": "Filter",
                "Refresh": "Refresh",
                
                "Operation completed successfully": "Operation completed successfully",
                "An error occurred": "An error occurred",
                "Loading...": "Loading...",
                "No data available": "No data available",
                
                "Just now": "Just now",
                "minutes ago": "minutes ago",
                "hours ago": "hours ago",
                "days ago": "days ago"
            }
        };
    }

    translate(key, language = null) {
        const lang = language || this.currentLanguage;
        
        if (this.translations[lang] && this.translations[lang][key]) {
            return this.translations[lang][key];
        }
        
        // Fallback to English if translation not found
        if (lang !== 'en' && this.translations.en && this.translations.en[key]) {
            return this.translations.en[key];
        }
        
        // Return the key itself if no translation found
        return key;
    }

    applyTranslations(language = null) {
        const lang = language || this.currentLanguage;
        
        // Find all elements with data-i18n attribute
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.translate(key, lang);
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else if (element.tagName === 'IMG' && element.getAttribute('alt')) {
                element.alt = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update page title if specified
        const titleKey = document.querySelector('title')?.getAttribute('data-i18n');
        if (titleKey) {
            document.title = this.translate(titleKey, lang);
        }

        // Update HTML lang attribute
        document.documentElement.lang = lang;

        // Trigger custom event for other components
        document.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: lang }
        }));
    }

    async setLanguage(language) {
        if (!this.translations[language]) {
            console.warn(`Language ${language} not available`);
            return false;
        }

        this.currentLanguage = language;
        this.saveLanguagePreference(language);
        this.applyTranslations(language);
        
        // Notify server about language change
        try {
            await fetch('/set_language/' + language, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } catch (error) {
            console.warn('Could not notify server about language change:', error);
        }

        return true;
    }

    saveLanguagePreference(language) {
        localStorage.setItem('preferredLanguage', language);
        
        // Also save in user profile if logged in
        if (window.currentUser) {
            // This would typically be done via an API call
            console.log('Saving language preference for user:', language);
        }
    }

    getStoredLanguage() {
        return localStorage.getItem('preferredLanguage') || 
               navigator.language.split('-')[0] || 
               'fr';
    }

    // Dynamic translation for JavaScript-generated content
    t(key, params = {}) {
        let translation = this.translate(key);
        
        // Replace parameters in translation
        Object.keys(params).forEach(param => {
            translation = translation.replace(`{${param}}`, params[param]);
        });
        
        return translation;
    }

    // Format numbers according to locale
    formatNumber(number, options = {}) {
        const locale = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
        
        return new Intl.NumberFormat(locale, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
            ...options
        }).format(number);
    }

    // Format currency according to locale
    formatCurrency(amount, currency = 'USD') {
        const locale = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
        
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Format date according to locale
    formatDate(date, options = {}) {
        const locale = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options })
            .format(new Date(date));
    }

    // Format time according to locale
    formatTime(date, options = {}) {
        const locale = this.currentLanguage === 'fr' ? 'fr-FR' : 'en-US';
        const defaultOptions = {
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options })
            .format(new Date(date));
    }

    // Relative time formatting (e.g., "2 hours ago")
    formatRelativeTime(date) {
        const now = new Date();
        const diffMs = now - new Date(date);
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 1) {
            return this.t('Just now');
        } else if (diffMins < 60) {
            return `${diffMins} ${this.t('minutes ago')}`;
        } else if (diffHours < 24) {
            return `${diffHours} ${this.t('hours ago')}`;
        } else {
            return `${diffDays} ${this.t('days ago')}`;
        }
    }

    // RTL support
    isRTL() {
        return ['ar', 'he', 'fa'].includes(this.currentLanguage);
    }

    // Get available languages
    getAvailableLanguages() {
        return Object.keys(this.translations).map(code => ({
            code: code,
            name: this.getLanguageName(code),
            nativeName: this.getNativeLanguageName(code)
        }));
    }

    getLanguageName(code) {
        const names = {
            'fr': 'French',
            'en': 'English',
            'es': 'Spanish',
            'de': 'German'
        };
        return names[code] || code;
    }

    getNativeLanguageName(code) {
        const names = {
            'fr': 'Français',
            'en': 'English',
            'es': 'Español',
            'de': 'Deutsch'
        };
        return names[code] || code;
    }

    // Add new translations dynamically
    addTranslations(language, newTranslations) {
        if (!this.translations[language]) {
            this.translations[language] = {};
        }
        
        Object.assign(this.translations[language], newTranslations);
        localStorage.setItem('appTranslations', JSON.stringify(this.translations));
        
        // Re-apply translations if this is the current language
        if (language === this.currentLanguage) {
            this.applyTranslations();
        }
    }

    // Export translations for backup
    exportTranslations() {
        const dataStr = JSON.stringify(this.translations, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `translations-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }
}

// Global translation function
function __(key, params = {}) {
    if (window.translationManager) {
        return window.translationManager.t(key, params);
    }
    return key;
}

// Initialize translation manager when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    window.translationManager = new TranslationManager();
    await window.translationManager.init();

    // Add language selector handler
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function(e) {
            window.translationManager.setLanguage(e.target.value);
        });
    }

    // Apply RTL if needed
    if (window.translationManager.isRTL()) {
        document.body.classList.add('rtl');
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TranslationManager, __ };
}