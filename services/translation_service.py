import json
import os

class TranslationService:
    def __init__(self):
        self.translations = self.load_translations()
    
    def load_translations(self):
        """Charge les fichiers de traduction"""
        translations = {}
        lang_dir = 'translations'
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(lang_dir, exist_ok=True)
        
        # Fichiers de traduction par défaut
        default_translations = {
            'fr': {
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
                "Total Predictions": "Total des Prédictions",
                "Fraud Cases": "Cas de Fraude",
                "Safe Transactions": "Transactions Sûres",
                "Fraud Rate": "Taux de Fraude",
                "High Risk": "Risque Élevé",
                "Medium Risk": "Risque Moyen",
                "Low Risk": "Risque Faible",
                "Transaction Amount": "Montant de la Transaction",
                "Currency": "Devise",
                "Analyze Transaction": "Analyser la Transaction",
                "Detection Results": "Résultats de la Détection",
                "Fraud Detected": "Fraude Détectée",
                "No Fraud Detected": "Aucune Fraude Détectée",
                "Confidence Level": "Niveau de Confiance",
                "Generate Report": "Générer un Rapport",
                "PDF Report": "Rapport PDF",
                "Excel Report": "Rapport Excel",
                "Admin Dashboard": "Tableau de Bord Admin",
                "User Management": "Gestion des Utilisateurs",
                "Model Management": "Gestion des Modèles",
                "Alert System": "Système d'Alerte"
            },
            'en': {
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
                "Total Predictions": "Total Predictions",
                "Fraud Cases": "Fraud Cases",
                "Safe Transactions": "Safe Transactions",
                "Fraud Rate": "Fraud Rate",
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
                "Generate Report": "Generate Report",
                "PDF Report": "PDF Report",
                "Excel Report": "Excel Report",
                "Admin Dashboard": "Admin Dashboard",
                "User Management": "User Management",
                "Model Management": "Model Management",
                "Alert System": "Alert System"
            }
        }
        
        # Sauvegarder les traductions par défaut
        for lang, trans_dict in default_translations.items():
            file_path = os.path.join(lang_dir, f'{lang}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(trans_dict, f, ensure_ascii=False, indent=2)
            translations[lang] = trans_dict
        
        # Charger les fichiers existants
        if os.path.exists(lang_dir):
            for lang_file in os.listdir(lang_dir):
                if lang_file.endswith('.json'):
                    lang_code = lang_file.split('.')[0]
                    try:
                        with open(os.path.join(lang_dir, lang_file), 'r', encoding='utf-8') as f:
                            translations[lang_code] = json.load(f)
                    except Exception as e:
                        print(f"Erreur chargement {lang_file}: {e}")
        
        return translations
    
    def get_translation(self, key, language='fr'):
        """Retourne la traduction pour une clé donnée"""
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        return key  # Retourne la clé si la traduction n'est pas trouvée
    
    def add_translation(self, key, translations_dict):
        """Ajoute une nouvelle traduction"""
        for lang, translation in translations_dict.items():
            if lang in self.translations:
                self.translations[lang][key] = translation
        
        # Sauvegarder les modifications
        self.save_translations()
    
    def save_translations(self):
        """Sauvegarde les traductions dans les fichiers"""
        lang_dir = 'translations'
        os.makedirs(lang_dir, exist_ok=True)
        
        for lang, trans_dict in self.translations.items():
            file_path = os.path.join(lang_dir, f'{lang}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(trans_dict, f, ensure_ascii=False, indent=2)