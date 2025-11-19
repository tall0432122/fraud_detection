from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.utils
import json
import logging
from config import Config

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application
app = Flask(__name__)
app.config.from_object(Config)

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Configuration de Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles de base de données étendus
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5), default='fr')
    last_login = db.Column(db.DateTime)
    
    # Relations
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True)
    alerts = db.relationship('Alert', backref='user', lazy=True)

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_data = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_fraud_confirmed = db.Column(db.Boolean, default=None)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModelPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    training_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Dictionnaire de traductions COMPLET
TRANSLATIONS = {
    'fr': {
        # Navigation
        'home': 'Accueil',
        'dashboard': 'Dashboard',
        'detection': 'Détection',
        'analysis': 'Analyses',
        'reports': 'Rapports',
        'batch_analysis': 'Analyse par Lots',
        'login': 'Connexion',
        'register': 'Inscription',
        'logout': 'Déconnexion',
        'profile': 'Profil',
        'admin_panel': 'Panel Admin',
        'train_model': 'Entraîner Modèle',
        
        # Page d'accueil
        'protect_business': 'Protégez votre entreprise contre la fraude',
        'advanced_features': 'Fonctionnalités Avancées de Détection de Fraude',
        'system_description': 'Système avancé de détection de fraude alimenté par l\'IA qui apprend et s\'adapte en temps réel pour protéger vos transactions financières.',
        'machine_learning_ai': 'IA par Apprentissage Automatique',
        'ml_description': 'Algorithmes avancés qui apprennent des modèles et s\'adaptent aux nouvelles techniques de fraude en temps réel.',
        'real_time_monitoring': 'Surveillance en Temps Réel',
        'rt_description': 'Détection instantanée et alertes pour les activités suspectes dès qu\'elles se produisent.',
        'advanced_analytics': 'Analyses Avancées',
        'aa_description': 'Outils complets de reporting et d\'analyse pour comprendre les modèles et tendances de fraude.',
        'multi_channel_alerts': 'Alertes Multi-canaux',
        'mca_description': 'Recevez des notifications instantanées par email, SMS ou alertes dans l\'application lorsque la fraude est détectée.',
        'batch_processing': 'Traitement par Lots',
        'bp_description': 'Analysez de grands volumes de transactions efficacement avec nos capacités de traitement par lots.',
        'multilingual_support': 'Support Multilingue',
        'ms_description': 'Interface entièrement localisée avec support de plusieurs langues et paramètres régionaux.',
        'detection_accuracy': 'Précision de Détection',
        'monitoring': 'Surveillance en Temps Réel',
        'response_time': 'Temps de Réponse',
        'fraud_patterns': 'Modèles de Fraude',
        'ready_to_secure': 'Prêt à sécuriser vos transactions ?',
        'join_businesses': 'Rejoignez des milliers d\'entreprises qui font confiance à notre système de détection de fraude pour protéger leurs opérations.',
        'fraudguard_system': 'Système intelligent de détection de fraude bancaire utilisant l\'IA.',
        'all_rights_reserved': 'Tous droits réservés',
        
        # Fonctionnalités détaillées
        'online_learning_capabilities': 'Capacités d\'apprentissage en ligne',
        'pattern_recognition': 'Reconnaissance de modèles',
        'anomaly_detection': 'Détection d\'anomalies',
        'instant_alerts': 'Alertes instantanées',
        'live_dashboards': 'Tableaux de bord en direct',
        'websocket_updates': 'Mises à jour WebSocket',
        'detailed_reports': 'Rapports détaillés',
        'trend_analysis': 'Analyse des tendances',
        'export_capabilities': 'Capacités d\'exportation',
        'email_notifications': 'Notifications par email',
        'sms_alerts': 'Alertes SMS',
        'in_app_notifications': 'Notifications dans l\'application',
        'csv_import': 'Import de fichiers CSV',
        'bulk_analysis': 'Analyse en masse',
        'background_processing': 'Traitement en arrière-plan',
        'french_english': 'Français & Anglais',
        'localized_content': 'Contenu localisé',
        'cultural_adaptation': 'Adaptation culturelle',
        
        # Messages flash
        'language_changed': 'Langue changée en',
        'login_success': 'Connexion réussie',
        'logout_success': 'Déconnexion réussie',
        'invalid_credentials': 'Identifiants incorrects',
        'username_taken': 'Nom d\'utilisateur déjà utilisé',
        'email_taken': 'Email déjà utilisé',
        'account_created': 'Compte créé avec succès',
        'access_denied': 'Accès non autorisé',
        'prediction_error': 'Erreur lors de la prédiction',
        'file_error': 'Erreur lors du traitement du fichier',
        'no_file_selected': 'Aucun fichier sélectionné',
        'csv_required': 'Veuillez sélectionner un fichier CSV',
        'model_trained': 'Modèle entraîné avec succès',
        'training_error': 'Erreur lors de l\'entraînement du modèle',
        'report_generated': 'Rapport généré avec succès',
        'report_error': 'Erreur génération rapport',
        'unsupported_report': 'Type de rapport non supporté',
        'export_error': 'Erreur lors de l\'export',
        'unsupported_format': 'Format non supporté',
        
        # Nouvelles traductions pour index.html
        'get_started': 'Commencer',
        'learn_more': 'En savoir plus',
        'system_combines': 'Notre système combine l\'apprentissage automatique avec la surveillance en temps réel pour fournir une protection complète contre la fraude.',
        'free_trial': 'Essai Gratuit',
        'analyze_transactions': 'Analyser les Transactions',
        'discover_system': 'Découvrez comment notre système protège votre entreprise',
        
        # Traductions pour base.html
        'fraud_detection': 'Détection de Fraude Bancaire',
        'master_dsgl': 'Master 1 DSGL',
        'university_bambey': 'Université Alloune Diop de Bambey',
        
        # Traductions générales
        'welcome': 'Bienvenue',
        'start_now': 'Commencer Maintenant',
        'go_to_dashboard': 'Aller au Tableau de Bord',
        'start_protection': 'Commencer la Protection',
        'start_detection': 'Démarrer la Détection',
        
        # Traductions pour login/register
        'username': 'Nom d\'utilisateur',
        'password': 'Mot de passe',
        'confirm_password': 'Confirmer le mot de passe',
        'email': 'Email',
        'remember_me': 'Se souvenir de moi',
        'forgot_password': 'Mot de passe oublié?',
        'no_account': 'Pas de compte?',
        'have_account': 'Déjà un compte?',
        'sign_in': 'Se connecter',
        'sign_up': 'S\'inscrire',
        'enter_username': 'Entrez votre nom d\'utilisateur',
        'enter_password': 'Entrez votre mot de passe',
        'welcome_back': 'Content de vous revoir',
        'login_to_account': 'Connectez-vous à votre compte FraudGuard',
        'register_here': 'Inscrivez-vous ici',
        'login_terms': 'En vous connectant, vous acceptez nos Conditions d\'utilisation et notre Politique de confidentialité',
        'demo_credentials': 'Identifiants de démonstration',
        'administrator': 'Administrateur',
        'user': 'Utilisateur',

        # Traductions pour register
        'create_account': 'Créer un compte',
        'join_fraudguard': 'Rejoignez FraudGuard pour sécuriser vos transactions',
        'choose_username': 'Choisissez un nom d\'utilisateur',
        'username_requirements': '3-20 caractères, lettres et chiffres uniquement',
        'your_email': 'votre@email.com',
        'create_password': 'Créez un mot de passe',
        'repeat_password': 'Répétez votre mot de passe',
        'phone_number': 'Numéro de téléphone',
        'optional': 'Optionnel',
        'phone_usage': 'Pour les alertes SMS et l\'authentification à deux facteurs',
        'accept_terms': 'J\'accepte les',
        'terms_of_use': 'Conditions d\'utilisation',
        'and': 'et la',
        'privacy_policy': 'Politique de confidentialité',
        'create_account_btn': 'Créer le compte',
        'login_here': 'Connectez-vous ici',
        'weak_password': 'Mot de passe faible',
        'medium_strength': 'Force moyenne',
        'strong_password': 'Mot de passe fort',
        'passwords_match': 'Les mots de passe correspondent',
        'passwords_dont_match': 'Les mots de passe ne correspondent pas',
        'passwords_dont_match_alert': 'Les mots de passe ne correspondent pas. Veuillez les vérifier.',
        'accept_terms_alert': 'Veuillez accepter les conditions d\'utilisation.',

        # Traductions pour les autres pages
        'my_profile': 'Mon Profil',
        'welcome_to_dashboard': 'Bienvenue sur votre Tableau de Bord',
        'total_predictions': 'Prédictions Totales',
        'fraud_cases': 'Cas de Fraude',
        'recent_activity': 'Activité Récente',
        'view_all': 'Voir Tout',
        'transaction': 'Transaction',
        'amount': 'Montant',
        'status': 'Statut',
        'date': 'Date',
        'fraud': 'Fraude',
        'non_fraud': 'Non Fraude',
        'secure': 'Sécurisé',
        'confidence': 'Confiance',
        'analysis_tools': 'Outils d\'Analyse',
        'generate_reports': 'Générer des Rapports',
        'language_settings': 'Paramètres de Langue',
        'current_language': 'Langue Actuelle',
        'choose_language': 'Choisir votre langue',
        'language_interface': 'Interface en langue',
        'select': 'Sélectionner',
        'current': 'Actuelle',
        'regional_settings': 'Paramètres Régionaux',
        'date_format': 'Format de date',
        'time_format': 'Format d\'heure',
        'number_format': 'Format des nombres',
        'default_currency': 'Devise par défaut',
        
        # NOUVELLES TRADUCTIONS AJOUTÉES
        'safe_transactions': 'Transactions Sécurisées',
        'fraud_rate': 'Taux de Fraude',
        'quick_actions': 'Actions Rapides',
        'single_analysis': 'Analyse Unique',
        'no_predictions_yet': 'Aucune prédiction pour le moment',
        'start_analyzing': 'Commencez à analyser vos transactions',
        'transaction_features': 'Caractéristiques de la Transaction',
        'analyze_transaction': 'Analyser la Transaction',
        'analysis_results': 'Résultats de l\'Analyse',
        'fraud_detected': 'Fraude Détectée',
        'transaction_safe': 'Transaction Sécurisée',
        'confidence_level': 'Niveau de Confiance',
        'transaction_details': 'Détails de la Transaction',
        'features_analyzed': 'Caractéristiques analysées',
        'analysis_time': 'Temps d\'analyse',
        'recent_analysis': 'Analyses Récentes',
        'no_recent_analysis': 'Aucune analyse récente',
        'currency': 'Devise',
        'analysis_coming_soon': 'Les outils d\'analyse avancée seront bientôt disponibles',
        'reports_coming_soon': 'La génération de rapports sera bientôt disponible',
        'back_to_detection': 'Retour à la Détection',
        'real_time_analytics': 'Analytics en Temps Réel',
        'today_transactions': 'Transactions Aujourd\'hui',
        'alert_rate': 'Taux d\'Alerte',
        'recent_alerts': 'Dernières Alertes',
        'no_recent_alerts': 'Aucune alerte récente',
        'recent_predictions': 'Dernières Prédictions',
        'new_analysis': 'Nouvelle Analyse',
        'result': 'Résultat',
        'pending': 'En attente',
        'confirmed': 'Confirmé',
        'validated': 'Validé',
        'active': 'Actif',
        'new': 'Nouveau',
        'registered_users': 'utilisateurs inscrits',
        'manage_users': 'Gérer les utilisateurs',
        'trained_models': 'modèles entraînés',
        'view_models': 'Voir les modèles',
        'total_analysis': 'analyses totales',
        'admin_dashboard': 'Tableau de bord admin',
        'advanced_analysis': 'Analyse Avancée',
        'accuracy_rate': 'Taux de précision',
        'no_analysis_data': 'Aucune donnée d\'analyse disponible',
        'start_analyzing_transactions': 'Commencez à analyser des transactions pour voir les analyses détaillées',
        'analyze_transactions': 'Analyser les transactions',
        'fraud_detection_trends': 'Tendances de détection de fraude',
        'prediction_distribution': 'Distribution des prédictions',
        'fraud_pattern_detection': 'Détection de patterns de fraude',
        'time_patterns': 'Patterns temporels',
        'fraud_activity_by_hour': 'Activité de fraude par heure',
        'risk_amounts': 'Montants à risque',
        'fraud_amount_distribution': 'Distribution des montants frauduleux',
        'geographic_areas': 'Zones géographiques',
        'risk_by_region': 'Risque par région',
        'normal_transactions': 'Transactions normales',
        'suspicious_transactions': 'Transactions suspectes',
        'to_verify': 'À vérifier',
        'mon': 'Lun',
        'tue': 'Mar',
        'wed': 'Mer',
        'thu': 'Jeu',
        'fri': 'Ven',
        'sat': 'Sam',
        'sun': 'Dim',
        'reports_analytics': 'Rapports & Analytics',
        'custom_report': 'Rapport Personnalisé',
        'pdf_report': 'Rapport PDF',
        'complete_report_with_charts': 'Rapport complet avec graphiques et analyse',
        'generate_pdf': 'Générer PDF',
        'excel_report': 'Rapport Excel',
        'detailed_spreadsheet_with_raw_data': 'Tableur détaillé avec données brutes',
        'generate_excel': 'Générer Excel',
        'performance_report': 'Rapport Performance',
        'model_performance_metrics': 'Métriques de performance du modèle',
        'generate': 'Générer',
        'scheduled_reports': 'Rapports Programmé',
        'automated_email_reports': 'Rapports automatisés par email',
        'configure': 'Configurer',
        'report_history': 'Historique des Rapports',
        'report_name': 'Nom du Rapport',
        'generated_on': 'Généré le',
        'size': 'Taille',
        'actions': 'Actions',
        'monthly_fraud_analysis': 'Analyse Mensuelle Fraude',
        'today_at': 'Aujourd\'hui à',
        'yesterday_at': 'Hier à',
        'schedule_automated_reports': 'Programmer Rapports Automatisés',
        'frequency': 'Fréquence',
        'daily': 'Quotidien',
        'weekly': 'Hebdomadaire',
        'monthly': 'Mensuel',
        'send_time': 'Heure d\'envoi',
        'report_format': 'Format du rapport',
        'enable_scheduled_reports': 'Activer les rapports programmés',
        'cancel': 'Annuler',
        'save': 'Sauvegarder',
        'custom_report_generation': 'Génération du rapport personnalisé...',
        'performance_report_generation': 'Génération du rapport de performance...',
        'schedule_saved': 'Programmation sauvegardée',
        'import_csv_file': 'Importer un fichier CSV',
        'select_csv_file': 'Sélectionner un fichier CSV',
        'expected_format': 'Format attendu',
        'columns_amount_features': 'colonnes amount, feature_1 à feature_13',
        'analyze_file': 'Analyser le Fichier',
        'expected_file_format': 'Format de Fichier Attendue',
        'your_csv_must_contain': 'Votre fichier CSV doit contenir les colonnes suivantes :',
        'column': 'Colonne',
        'description': 'Description',
        'example': 'Exemple',
        'transaction_amount': 'Montant de la transaction',
        'feature': 'Caractéristique',
        'download_example': 'Télécharger un exemple',
        'analysis_tips': 'Conseils d\'Analyse',
        'standard_csv_format': 'Format CSV standard avec en-têtes',
        'max_transactions_per_file': 'Maximum 10,000 transactions par fichier',
        'analysis_time_per_transaction': 'Temps d\'analyse: ~1 seconde par transaction',
        'exportable_results': 'Résultats exportables en PDF/Excel',
        'tip': 'Astuce',
        'features_tip': 'Les caractéristiques (features) doivent être des valeurs numériques normalisées entre -1 et 1.',
        'recent_statistics': 'Statistiques Récentes',
        'batch_analysis_results': 'Résultats de l\'Analyse par Lots',
        'analyzed_transactions': 'Transactions analysées',
        'fraudulent_transactions': 'Transactions frauduleuses',
        'search': 'Rechercher',
        'all_statuses': 'Tous les statuts',
        'all_confidence': 'Toutes les confiances',
        'high_confidence': 'Haute confiance',
        'medium_confidence': 'Confiance moyenne',
        'low_confidence': 'Basse confiance',
        'transaction_id': 'ID Transaction',
        'normal': 'Normal',
        'export_csv': 'Exporter CSV',
        'generate_report': 'Générer Rapport',
        'csv_export_functionality': 'Fonctionnalité d\'export CSV à implémenter',
        'pdf_report_functionality': 'Fonctionnalité de rapport PDF à implémenter',
        'users': 'Utilisateurs',
        'statistics': 'Statistiques',
        'models': 'Modèles',
        'transactions': 'Transactions',
        'alerts': 'Alertes'
    },
    'en': {
        # Navigation
        'home': 'Home',
        'dashboard': 'Dashboard',
        'detection': 'Detection',
        'analysis': 'Analysis',
        'reports': 'Reports',
        'batch_analysis': 'Batch Analysis',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'profile': 'Profile',
        'admin_panel': 'Admin Panel',
        'train_model': 'Train Model',
        
        # Page d'accueil
        'protect_business': 'Protect your business from fraud',
        'advanced_features': 'Advanced Fraud Detection Features',
        'system_description': 'Advanced AI-powered fraud detection system that learns and adapts in real-time to protect your financial transactions.',
        'machine_learning_ai': 'Machine Learning AI',
        'ml_description': 'Advanced algorithms that learn patterns and adapt to new fraud techniques in real-time.',
        'real_time_monitoring': 'Real-Time Monitoring',
        'rt_description': 'Instant detection and alerts for suspicious activities as they happen.',
        'advanced_analytics': 'Advanced Analytics',
        'aa_description': 'Comprehensive reporting and analysis tools to understand fraud patterns and trends.',
        'multi_channel_alerts': 'Multi-Channel Alerts',
        'mca_description': 'Receive instant notifications via email, SMS, or in-app alerts when fraud is detected.',
        'batch_processing': 'Batch Processing',
        'bp_description': 'Efficiently analyze large volumes of transactions with our batch processing capabilities.',
        'multilingual_support': 'Multilingual Support',
        'ms_description': 'Fully localized interface with support for multiple languages and regional settings.',
        'detection_accuracy': 'Detection Accuracy',
        'monitoring': '24/7 Monitoring',
        'response_time': 'Response Time',
        'fraud_patterns': 'Fraud Patterns',
        'ready_to_secure': 'Ready to secure your transactions?',
        'join_businesses': 'Join thousands of businesses that trust our fraud detection system to protect their operations.',
        'fraudguard_system': 'Intelligent banking fraud detection system using AI.',
        'all_rights_reserved': 'All rights reserved',
        
        # Fonctionnalités détaillées
        'online_learning_capabilities': 'Online learning capabilities',
        'pattern_recognition': 'Pattern recognition',
        'anomaly_detection': 'Anomaly detection',
        'instant_alerts': 'Instant alerts',
        'live_dashboards': 'Live dashboards',
        'websocket_updates': 'WebSocket updates',
        'detailed_reports': 'Detailed reports',
        'trend_analysis': 'Trend analysis',
        'export_capabilities': 'Export capabilities',
        'email_notifications': 'Email notifications',
        'sms_alerts': 'SMS alerts',
        'in_app_notifications': 'In-app notifications',
        'csv_import': 'CSV file import',
        'bulk_analysis': 'Bulk analysis',
        'background_processing': 'Background processing',
        'french_english': 'French & English',
        'localized_content': 'Localized content',
        'cultural_adaptation': 'Cultural adaptation',
        
        # Messages flash
        'language_changed': 'Language changed to',
        'login_success': 'Login successful',
        'logout_success': 'Logout successful',
        'invalid_credentials': 'Invalid credentials',
        'username_taken': 'Username already taken',
        'email_taken': 'Email already taken',
        'account_created': 'Account created successfully',
        'access_denied': 'Access denied',
        'prediction_error': 'Error during prediction',
        'file_error': 'Error processing file',
        'no_file_selected': 'No file selected',
        'csv_required': 'Please select a CSV file',
        'model_trained': 'Model trained successfully',
        'training_error': 'Error during model training',
        'report_generated': 'Report generated successfully',
        'report_error': 'Report generation error',
        'unsupported_report': 'Unsupported report type',
        'export_error': 'Error during export',
        'unsupported_format': 'Unsupported format',
        
        # Nouvelles traductions pour index.html
        'get_started': 'Get Started',
        'learn_more': 'Learn More',
        'system_combines': 'Our system combines machine learning with real-time monitoring to provide comprehensive fraud protection.',
        'free_trial': 'Free Trial',
        'analyze_transactions': 'Analyze Transactions',
        'discover_system': 'Discover how our system protects your business',
        
        # Traductions pour base.html
        'fraud_detection': 'Banking Fraud Detection',
        'master_dsgl': 'Master 1 DSGL',
        'university_bambey': 'Alloune Diop University of Bambey',
        
        # Traductions générales
        'welcome': 'Welcome',
        'start_now': 'Start Now',
        'go_to_dashboard': 'Go to Dashboard',
        'start_protection': 'Start Protection',
        'start_detection': 'Start Detection',
        
        # Traductions pour login/register
        'username': 'Username',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'email': 'Email',
        'remember_me': 'Remember me',
        'forgot_password': 'Forgot password?',
        'no_account': 'Don\'t have an account?',
        'have_account': 'Already have an account?',
        'sign_in': 'Sign In',
        'sign_up': 'Sign Up',
        'enter_username': 'Enter your username',
        'enter_password': 'Enter your password',
        'welcome_back': 'Welcome back',
        'login_to_account': 'Login to your FraudGuard account',
        'register_here': 'Register here',
        'login_terms': 'By logging in, you accept our Terms of Use and Privacy Policy',
        'demo_credentials': 'Demo credentials',
        'administrator': 'Administrator',
        'user': 'User',

        # Traductions pour register
        'create_account': 'Create Account',
        'join_fraudguard': 'Join FraudGuard to secure your transactions',
        'choose_username': 'Choose a username',
        'username_requirements': '3-20 characters, letters and numbers only',
        'your_email': 'your@email.com',
        'create_password': 'Create a password',
        'repeat_password': 'Repeat your password',
        'phone_number': 'Phone number',
        'optional': 'Optional',
        'phone_usage': 'For SMS alerts and two-factor authentication',
        'accept_terms': 'I accept the',
        'terms_of_use': 'Terms of Use',
        'and': 'and the',
        'privacy_policy': 'Privacy Policy',
        'create_account_btn': 'Create Account',
        'login_here': 'Login here',
        'weak_password': 'Weak password',
        'medium_strength': 'Medium strength',
        'strong_password': 'Strong password',
        'passwords_match': 'Passwords match',
        'passwords_dont_match': 'Passwords don\'t match',
        'passwords_dont_match_alert': 'Passwords do not match. Please check them.',
        'accept_terms_alert': 'Please accept the terms of use.',

        # Traductions pour les autres pages
        'my_profile': 'My Profile',
        'welcome_to_dashboard': 'Welcome to your Dashboard',
        'total_predictions': 'Total Predictions',
        'fraud_cases': 'Fraud Cases',
        'recent_activity': 'Recent Activity',
        'view_all': 'View All',
        'transaction': 'Transaction',
        'amount': 'Amount',
        'status': 'Status',
        'date': 'Date',
        'fraud': 'Fraud',
        'non_fraud': 'Non Fraud',
        'secure': 'Secure',
        'confidence': 'Confidence',
        'analysis_tools': 'Analysis Tools',
        'generate_reports': 'Generate Reports',
        'language_settings': 'Language Settings',
        'current_language': 'Current Language',
        'choose_language': 'Choose your language',
        'language_interface': 'language interface',
        'select': 'Select',
        'current': 'Current',
        'regional_settings': 'Regional Settings',
        'date_format': 'Date format',
        'time_format': 'Time format',
        'number_format': 'Number format',
        'default_currency': 'Default currency',
        
        # NOUVELLES TRADUCTIONS AJOUTÉES
        'safe_transactions': 'Safe Transactions',
        'fraud_rate': 'Fraud Rate',
        'quick_actions': 'Quick Actions',
        'single_analysis': 'Single Analysis',
        'no_predictions_yet': 'No predictions yet',
        'start_analyzing': 'Start analyzing your transactions',
        'transaction_features': 'Transaction Features',
        'analyze_transaction': 'Analyze Transaction',
        'analysis_results': 'Analysis Results',
        'fraud_detected': 'Fraud Detected',
        'transaction_safe': 'Transaction Safe',
        'confidence_level': 'Confidence Level',
        'transaction_details': 'Transaction Details',
        'features_analyzed': 'Features analyzed',
        'analysis_time': 'Analysis time',
        'recent_analysis': 'Recent Analysis',
        'no_recent_analysis': 'No recent analysis',
        'currency': 'Currency',
        'analysis_coming_soon': 'Advanced analysis tools coming soon',
        'reports_coming_soon': 'Report generation coming soon',
        'back_to_detection': 'Back to Detection',
        'real_time_analytics': 'Real-Time Analytics',
        'today_transactions': 'Today Transactions',
        'alert_rate': 'Alert Rate',
        'recent_alerts': 'Recent Alerts',
        'no_recent_alerts': 'No recent alerts',
        'recent_predictions': 'Recent Predictions',
        'new_analysis': 'New Analysis',
        'result': 'Result',
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'validated': 'Validated',
        'active': 'Active',
        'new': 'New',
        'registered_users': 'registered users',
        'manage_users': 'Manage users',
        'trained_models': 'trained models',
        'view_models': 'View models',
        'total_analysis': 'total analysis',
        'admin_dashboard': 'Admin dashboard',
        'advanced_analysis': 'Advanced Analysis',
        'accuracy_rate': 'Accuracy Rate',
        'no_analysis_data': 'No analysis data available',
        'start_analyzing_transactions': 'Start analyzing transactions to see detailed analysis and insights',
        'analyze_transactions': 'Analyze transactions',
        'fraud_detection_trends': 'Fraud Detection Trends',
        'prediction_distribution': 'Prediction Distribution',
        'fraud_pattern_detection': 'Fraud Pattern Detection',
        'time_patterns': 'Time patterns',
        'fraud_activity_by_hour': 'Fraud activity by hour',
        'risk_amounts': 'Risk amounts',
        'fraud_amount_distribution': 'Fraud amount distribution',
        'geographic_areas': 'Geographic areas',
        'risk_by_region': 'Risk by region',
        'normal_transactions': 'Normal transactions',
        'suspicious_transactions': 'Suspicious transactions',
        'to_verify': 'To verify',
        'mon': 'Mon',
        'tue': 'Tue',
        'wed': 'Wed',
        'thu': 'Thu',
        'fri': 'Fri',
        'sat': 'Sat',
        'sun': 'Sun',
        'reports_analytics': 'Reports & Analytics',
        'custom_report': 'Custom Report',
        'pdf_report': 'PDF Report',
        'complete_report_with_charts': 'Complete report with charts and analysis',
        'generate_pdf': 'Generate PDF',
        'excel_report': 'Excel Report',
        'detailed_spreadsheet_with_raw_data': 'Detailed spreadsheet with raw data',
        'generate_excel': 'Generate Excel',
        'performance_report': 'Performance Report',
        'model_performance_metrics': 'Model performance metrics',
        'generate': 'Generate',
        'scheduled_reports': 'Scheduled Reports',
        'automated_email_reports': 'Automated email reports',
        'configure': 'Configure',
        'report_history': 'Report History',
        'report_name': 'Report Name',
        'generated_on': 'Generated on',
        'size': 'Size',
        'actions': 'Actions',
        'monthly_fraud_analysis': 'Monthly Fraud Analysis',
        'today_at': 'Today at',
        'yesterday_at': 'Yesterday at',
        'schedule_automated_reports': 'Schedule Automated Reports',
        'frequency': 'Frequency',
        'daily': 'Daily',
        'weekly': 'Weekly',
        'monthly': 'Monthly',
        'send_time': 'Send time',
        'report_format': 'Report format',
        'enable_scheduled_reports': 'Enable scheduled reports',
        'cancel': 'Cancel',
        'save': 'Save',
        'custom_report_generation': 'Custom report generation...',
        'performance_report_generation': 'Performance report generation...',
        'schedule_saved': 'Schedule saved',
        'import_csv_file': 'Import CSV File',
        'select_csv_file': 'Select CSV file',
        'expected_format': 'Expected format',
        'columns_amount_features': 'columns amount, feature_1 to feature_13',
        'analyze_file': 'Analyze File',
        'expected_file_format': 'Expected File Format',
        'your_csv_must_contain': 'Your CSV file must contain the following columns:',
        'column': 'Column',
        'description': 'Description',
        'example': 'Example',
        'transaction_amount': 'Transaction amount',
        'feature': 'Feature',
        'download_example': 'Download example',
        'analysis_tips': 'Analysis Tips',
        'standard_csv_format': 'Standard CSV format with headers',
        'max_transactions_per_file': 'Maximum 10,000 transactions per file',
        'analysis_time_per_transaction': 'Analysis time: ~1 second per transaction',
        'exportable_results': 'Exportable results in PDF/Excel',
        'tip': 'Tip',
        'features_tip': 'Features must be numeric values normalized between -1 and 1.',
        'recent_statistics': 'Recent Statistics',
        'batch_analysis_results': 'Batch Analysis Results',
        'analyzed_transactions': 'Analyzed transactions',
        'fraudulent_transactions': 'Fraudulent transactions',
        'search': 'Search',
        'all_statuses': 'All statuses',
        'all_confidence': 'All confidence',
        'high_confidence': 'High confidence',
        'medium_confidence': 'Medium confidence',
        'low_confidence': 'Low confidence',
        'transaction_id': 'Transaction ID',
        'normal': 'Normal',
        'export_csv': 'Export CSV',
        'generate_report': 'Generate Report',
        'csv_export_functionality': 'CSV export functionality to implement',
        'pdf_report_functionality': 'PDF report functionality to implement',
        'users': 'Users',
        'statistics': 'Statistics',
        'models': 'Models',
        'transactions': 'Transactions',
        'alerts': 'Alerts'
    }
}

def _(text):
    """Fonction de traduction améliorée"""
    locale = get_locale()
    # Cherche la traduction, sinon retourne le texte original
    return TRANSLATIONS.get(locale, {}).get(text, text)

def get_locale():
    """Détermine la langue actuelle"""
    try:
        if current_user.is_authenticated and hasattr(current_user, 'language') and current_user.language:
            return current_user.language
    except:
        pass
    
    if 'language' in session and session['language'] in ['fr', 'en']:
        return session['language']
    
    return 'fr'  # Français par défaut

# Passez la fonction _ aux templates
@app.context_processor
def utility_processor():
    return dict(_=_, get_locale=get_locale)

# Import des services avec gestion d'erreur
try:
    from services.email_service import EmailService
    from services.sms_service import SMSService
    from services.bank_api import BankAPIService
    from services.report_generator import ReportGenerator
    from services.translation_service import TranslationService
    from model.online_learner import OnlineLearner
    
    email_service = EmailService(app)
    sms_service = SMSService(app)
    bank_api = BankAPIService(app)
    report_generator = ReportGenerator()
    translator = TranslationService()
    online_learner = OnlineLearner()
    
except ImportError as e:
    logger.warning(f"Services non disponibles: {e}")
    class DummyService:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    email_service = DummyService()
    sms_service = DummyService()
    bank_api = DummyService()
    report_generator = DummyService()
    translator = DummyService()
    online_learner = DummyService()

# Tâches Celery
@celery.task
def send_alert_async(user_id, alert_type, message, severity='medium'):
    try:
        user = User.query.get(user_id)
        if user:
            alert = Alert(
                user_id=user_id,
                type=alert_type,
                message=message,
                severity=severity
            )
            db.session.add(alert)
            
            if alert_type in ['email', 'both'] and user.email:
                email_service.send_alert(user.email, message, severity)
            
            if alert_type in ['sms', 'both'] and user.phone:
                sms_service.send_alert(user.phone, message)
            
            alert.is_sent = True
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Erreur envoi alerte: {str(e)}")

@celery.task
def update_model_async(feedback_data):
    try:
        online_learner.partial_fit(feedback_data)
        logger.info("Modèle mis à jour avec succès")
    except Exception as e:
        logger.error(f"Erreur mise à jour modèle: {str(e)}")

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['fr', 'en']:
        if current_user.is_authenticated:
            current_user.language = language
            db.session.commit()
        else:
            session['language'] = language
        flash(f"{_('language_changed')} {language}", 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(_('login_success'), 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(_('invalid_credentials'), 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash(_('username_taken'), 'error')
        elif User.query.filter_by(email=email).first():
            flash(_('email_taken'), 'error')
        else:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash(_('account_created'), 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_predictions = PredictionHistory.query.filter_by(user_id=current_user.id).count()
    user_frauds = PredictionHistory.query.filter_by(user_id=current_user.id, prediction='Fraude').count()
    recent_predictions = PredictionHistory.query.filter_by(user_id=current_user.id).order_by(PredictionHistory.created_at.desc()).limit(5).all()
    
    # Variables pour la section admin
    total_users = User.query.count()
    total_predictions = PredictionHistory.query.count()
    model_performance = ModelPerformance.query.order_by(ModelPerformance.training_date.desc()).limit(5).all()
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         user_predictions=user_predictions,
                         user_frauds=user_frauds,
                         recent_predictions=recent_predictions,
                         total_users=total_users,
                         total_predictions=total_predictions,
                         model_performance=model_performance,
                         recent_alerts=recent_alerts)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('logout_success'), 'success')
    return redirect(url_for('index'))

# Routes pour les fonctionnalités principales
@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    # Récupérer les prédictions récentes pour l'affichage
    recent_predictions = PredictionHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(PredictionHistory.created_at.desc()).limit(5).all()
    
    if request.method == 'POST':
        try:
            transaction_data = {}
            features = []
            
            for i in range(1, 14):
                feature_name = f'feature_{i}'
                value = float(request.form.get(feature_name, 0))
                features.append(value)
                transaction_data[feature_name] = value
            
            amount = float(request.form.get('amount', 0))
            currency = request.form.get('currency', 'USD')
            
            # Mode démo (modèle non disponible)
            is_fraud = np.random.choice([True, False], p=[0.1, 0.9])
            confidence = np.random.uniform(0.7, 0.99) if is_fraud else np.random.uniform(0.8, 0.95)
            
            history = PredictionHistory(
                user_id=current_user.id,
                transaction_data=json.dumps(transaction_data),
                prediction='Fraude' if is_fraud else 'Non Fraude',
                confidence=confidence,
                amount=amount,
                currency=currency
            )
            db.session.add(history)
            db.session.commit()
            
            if is_fraud and confidence > 0.8:
                alert_message = f"Alerte Fraude: Transaction de {amount} {currency} détectée avec {confidence:.2%} de confiance"
                send_alert_async.delay(current_user.id, 'both', alert_message, 'high')
            
            return render_template('prediction.html', 
                                prediction=is_fraud,
                                confidence=confidence,
                                features=features,
                                amount=amount,
                                currency=currency,
                                recent_predictions=recent_predictions,
                                show_results=True)
            
        except Exception as e:
            flash(_('prediction_error'), 'error')
            logger.error(f"Erreur prédiction: {str(e)}")
            return render_template('prediction.html', 
                                recent_predictions=recent_predictions,
                                show_results=False)
    
    return render_template('prediction.html', 
                         recent_predictions=recent_predictions,
                         show_results=False)

@app.route('/advanced-analysis')
@login_required
def advanced_analysis():
    """Page d'analyse avancée"""
    user_predictions = PredictionHistory.query.filter_by(user_id=current_user.id).count()
    user_frauds = PredictionHistory.query.filter_by(user_id=current_user.id, prediction='Fraude').count()
    
    has_data = user_predictions > 0
    
    return render_template('analysis.html', 
                         has_data=has_data,
                         user_predictions=user_predictions,
                         user_frauds=user_frauds)

@app.route('/reports-dashboard')
@login_required
def reports_dashboard():
    """Page des rapports"""
    return render_template('reports.html')

@app.route('/language-preferences')
@login_required
def language_preferences():
    """Page des paramètres de langue"""
    return render_template('multilingual.html')

@app.route('/user-profile')
@login_required
def user_profile():
    """Page de profil utilisateur"""
    total_predictions = PredictionHistory.query.filter_by(user_id=current_user.id).count()
    safe_predictions = PredictionHistory.query.filter_by(user_id=current_user.id, prediction='Non Fraude').count()
    fraud_predictions = PredictionHistory.query.filter_by(user_id=current_user.id, prediction='Fraude').count()
    
    recent_predictions = PredictionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(PredictionHistory.created_at.desc())\
        .limit(5)\
        .all()
    
    account_age = (datetime.utcnow() - current_user.created_at).days
    
    return render_template('profile.html',
                         total_predictions=total_predictions,
                         safe_predictions=safe_predictions,
                         fraud_predictions=fraud_predictions,
                         recent_predictions=recent_predictions,
                         account_age=account_age)

# Routes administratives
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash(_('access_denied'), 'error')
        return redirect(url_for('dashboard'))
    
    total_users = User.query.count()
    total_predictions = PredictionHistory.query.count()
    total_frauds = PredictionHistory.query.filter_by(prediction='Fraude').count()
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(10).all()
    model_performance = ModelPerformance.query.order_by(ModelPerformance.training_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_predictions=total_predictions,
                         total_frauds=total_frauds,
                         recent_alerts=recent_alerts,
                         model_performance=model_performance)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash(_('access_denied'), 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/models')
@login_required
def admin_models():
    if not current_user.is_admin:
        flash(_('access_denied'), 'error')
        return redirect(url_for('dashboard'))
    
    models = ModelPerformance.query.order_by(ModelPerformance.training_date.desc()).all()
    return render_template('admin/models.html', models=models)

@app.route('/admin/alerts')
@login_required
def admin_alerts():
    if not current_user.is_admin:
        flash(_('access_denied'), 'error')
        return redirect(url_for('dashboard'))
    
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
    return render_template('admin/alerts.html', alerts=alerts)

# Routes pour la génération de rapports
@app.route('/generate-report/<report_type>')
@login_required
def generate_report(report_type):
    """Générer un rapport"""
    try:
        if report_type == 'pdf':
            # Simulation de génération PDF
            flash(_('report_generated'), 'success')
        elif report_type == 'excel':
            # Simulation de génération Excel
            flash(_('report_generated'), 'success')
        else:
            flash(_('unsupported_report'), 'error')
    except Exception as e:
        flash(_('report_error'), 'error')
        logger.error(f"Erreur génération rapport: {str(e)}")
    
    return redirect(url_for('reports_dashboard'))

# API pour les données d'analyse
@app.route('/api/analysis/data')
@login_required
def get_analysis_data():
    """API pour les données d'analyse"""
    date_range = request.args.get('range', '30days')
    
    # Simuler des données d'analyse
    data = {
        'metrics': {
            'total_predictions': 150,
            'fraud_cases': 23,
            'accuracy_rate': 98.2,
            'avg_confidence': 92.5,
            'prediction_trend': 5.2,
            'fraud_trend': -2.1,
            'accuracy_trend': 1.5,
            'confidence_trend': 0.8
        },
        'charts': {
            'trend': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'fraud_data': [12, 19, 8, 15, 12, 18],
                'total_data': [45, 52, 48, 55, 50, 53]
            },
            'distribution': [70, 30]
        },
        'statistics': [
            {'metric': 'Transactions totales', 'current': '150', 'previous': '142', 'change': '+8', 'trend': 5.6},
            {'metric': 'Taux de fraude', 'current': '15.3%', 'previous': '16.8%', 'change': '-1.5%', 'trend': -8.9},
            {'metric': 'Précision moyenne', 'current': '98.2%', 'previous': '97.5%', 'change': '+0.7%', 'trend': 0.7}
        ],
        'patterns': {
            'common_fraud_time': '14:00-16:00',
            'peak_activity_hours': '10:00-12:00, 14:00-16:00',
            'avg_fraud_amount': '$245.67',
            'high_risk_amount_range': '$200-$500',
            'high_risk_locations': 'International',
            'suspicious_ips': '3 adresses détectées'
        }
    }
    
    return jsonify(data)

# API pour feedback d'apprentissage
@app.route('/api/feedback', methods=['POST'])
@login_required
def provide_feedback():
    try:
        data = request.get_json()
        prediction_id = data.get('prediction_id')
        is_correct = data.get('is_correct')
        actual_label = data.get('actual_label')
        
        prediction = PredictionHistory.query.get(prediction_id)
        if prediction and prediction.user_id == current_user.id:
            prediction.is_fraud_confirmed = actual_label == 1
            
            # Préparation des données pour l'apprentissage en ligne
            features = json.loads(prediction.transaction_data)
            feature_values = list(features.values())
            
            feedback_data = {
                'features': [feature_values],
                'labels': [actual_label]
            }
            
            # Mise à jour asynchrone du modèle
            update_model_async.delay(feedback_data)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Feedback enregistré'})
        
        return jsonify({'success': False, 'message': 'Prédiction non trouvée'})
    
    except Exception as e:
        logger.error(f"Erreur feedback: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur serveur'})

# API pour intégration bancaire
@app.route('/api/bank/transactions', methods=['GET'])
@login_required
def get_bank_transactions():
    try:
        account_id = request.args.get('account_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Simulation de données bancaires
        transactions = [
            {
                'id': 1,
                'date': '2024-01-15',
                'amount': 150.75,
                'description': 'Achat en ligne',
                'merchant': 'Amazon',
                'category': 'Shopping'
            },
            {
                'id': 2,
                'date': '2024-01-14',
                'amount': 45.50,
                'description': 'Restaurant',
                'merchant': 'Pizza Hut',
                'category': 'Nourriture'
            }
        ]
        
        return jsonify({'success': True, 'transactions': transactions})
    
    except Exception as e:
        logger.error(f"Erreur API bancaire: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur connexion banque'})

@app.route('/batch-prediction', methods=['GET', 'POST'])
@login_required
def batch_prediction():
    """Analyse par lots avec fichier CSV"""
    if request.method == 'POST':
        try:
            if 'csv_file' not in request.files:
                flash(_('no_file_selected'), 'error')
                return redirect(url_for('batch_prediction'))
            
            file = request.files['csv_file']
            if file.filename == '':
                flash(_('no_file_selected'), 'error')
                return redirect(url_for('batch_prediction'))
            
            if file and file.filename.endswith('.csv'):
                # Lire le fichier CSV
                df = pd.read_csv(file)
                
                # Simulation d'analyse
                results = []
                for index, row in df.iterrows():
                    is_fraud = np.random.choice([True, False], p=[0.15, 0.85])
                    confidence = np.random.uniform(0.7, 0.99) if is_fraud else np.random.uniform(0.8, 0.95)
                    
                    results.append({
                        'transaction_id': index + 1,
                        'amount': row.get('amount', 0) if 'amount' in row else np.random.uniform(10, 1000),
                        'prediction': 'Fraude' if is_fraud else 'Sécurisé',
                        'confidence': confidence
                    })
                
                return render_template('batch_results.html', results=results)
            else:
                flash(_('csv_required'), 'error')
                
        except Exception as e:
            flash(_('file_error'), 'error')
            logger.error(f"Erreur analyse par lots: {str(e)}")
    
    return render_template('batch_prediction.html')

# NOUVELLE ROUTE AJOUTÉE
@app.route('/batch-results')
@login_required
def batch_results():
    """Page des résultats d'analyse par lots"""
    # Cette route devrait être appelée après le traitement par lots
    # Pour l'instant, on simule des résultats
    results = [
        {
            'transaction_id': i + 1,
            'amount': round(np.random.uniform(10, 1000), 2),
            'prediction': 'Fraude' if np.random.random() < 0.15 else 'Sécurisé',
            'confidence': round(np.random.uniform(0.7, 0.99), 3)
        }
        for i in range(10)
    ]
    
    return render_template('batch_results.html', results=results)

@app.route('/analysis')
@login_required
def analysis():
    """Alias pour advanced_analysis pour la compatibilité"""
    return redirect(url_for('advanced_analysis'))

@app.route('/reports')
@login_required
def reports():
    """Alias pour reports_dashboard pour la compatibilité"""
    return redirect(url_for('reports_dashboard'))

@app.route('/export-results/<format_type>')
@login_required
def export_results(format_type):
    """Exporter les résultats d'analyse"""
    try:
        # Récupérer les résultats de la session ou les regénérer
        # Pour l'instant, on simule l'export
        if format_type == 'csv':
            flash(_('report_generated'), 'success')
            # Retourner un fichier CSV simulé
            return "ID,Montant,Prédiction,Confiance\n1,100.50,Sécurisé,85.2%", 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=resultats_analyse.csv'
            }
        elif format_type == 'pdf':
            flash(_('report_generated'), 'success')
        else:
            flash(_('unsupported_format'), 'error')
    except Exception as e:
        flash(_('export_error'), 'error')
        logger.error(f"Erreur export: {str(e)}")
    
    return redirect(url_for('batch_prediction'))

@app.route('/multilingual')
@login_required
def multilingual():
    """Alias pour language_preferences pour la compatibilité"""
    return redirect(url_for('language_preferences'))

@app.route('/profile')
@login_required
def profile():
    """Alias pour user_profile pour la compatibilité"""
    return redirect(url_for('user_profile'))

# Route pour l'entraînement du modèle
@app.route('/train-model')
@login_required
def train_model():
    if not current_user.is_admin:
        flash(_('access_denied'), 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Simulation d'entraînement de modèle
        model_perf = ModelPerformance(
            model_name='Random Forest v2.0',
            accuracy=0.982,
            precision=0.968,
            recall=0.955,
            f1_score=0.961,
            is_active=True
        )
        db.session.add(model_perf)
        db.session.commit()
        
        flash(_('model_trained'), 'success')
    except Exception as e:
        flash(_('training_error'), 'error')
        logger.error(f"Erreur entraînement modèle: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username='admin',
                email=app.config.get('ADMIN_EMAIL', 'admin@example.com'),
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Administrateur par défaut créé")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)