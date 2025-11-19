import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, app):
        self.mail = Mail(app)
        self.app = app
    
    def send_alert(self, recipient, message, severity='medium'):
        """Envoie une alerte par email"""
        try:
            subject = f"🚨 Alerte Fraude - {severity.upper()}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert {{ padding: 20px; border-radius: 5px; }}
                    .high {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
                    .medium {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
                    .low {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
                </style>
            </head>
            <body>
                <div class="alert {severity}">
                    <h2>🚨 Alerte de Détection de Fraude</h2>
                    <p><strong>Niveau:</strong> {severity.upper()}</p>
                    <p><strong>Message:</strong> {message}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <br>
                    <p><em>Ceci est une alerte automatique du système FraudGuard.</em></p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_content,
                sender=self.app.config.get('MAIL_DEFAULT_SENDER', 'noreply@fraudguard.com')
            )
            
            self.mail.send(msg)
            logger.info(f"Alerte email envoyée à {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {str(e)}")
            return False
    
    def send_daily_report(self, recipient, report_data):
        """Envoie un rapport quotidien"""
        try:
            subject = "📊 Rapport Quotidien - Détection de Fraude"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .report {{ padding: 20px; background-color: #f5f5f5; }}
                    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
                    .stat-card {{ background: white; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="report">
                    <h2>📊 Rapport Quotidien - FraudGuard</h2>
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Total Transactions</h3>
                            <p>{report_data.get('total_transactions', 0)}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Fraudes Détectées</h3>
                            <p>{report_data.get('fraud_cases', 0)}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Taux de Fraude</h3>
                            <p>{report_data.get('fraud_rate', 0):.2f}%</p>
                        </div>
                        <div class="stat-card">
                            <h3>Confiance Moyenne</h3>
                            <p>{report_data.get('avg_confidence', 0):.2f}%</p>
                        </div>
                    </div>
                    <p><em>Rapport généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_content,
                sender=self.app.config.get('MAIL_DEFAULT_SENDER', 'noreply@fraudguard.com')
            )
            
            self.mail.send(msg)
            logger.info(f"Rapport quotidien envoyé à {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi rapport: {str(e)}")
            return False

    def send_welcome_email(self, recipient, username):
        """Envoie un email de bienvenue à un nouvel utilisateur"""
        try:
            subject = "👋 Bienvenue sur FraudGuard"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .welcome {{ padding: 20px; background-color: #e3f2fd; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="welcome">
                    <h2>Bienvenue sur FraudGuard !</h2>
                    <p>Cher(e) <strong>{username}</strong>,</p>
                    <p>Votre compte a été créé avec succès sur notre plateforme de détection de fraude.</p>
                    <p>Vous pouvez maintenant :</p>
                    <ul>
                        <li>Analyser des transactions individuelles</li>
                        <li>Effectuer des analyses par lots</li>
                        <li>Consulter vos rapports détaillés</li>
                        <li>Recevoir des alertes en temps réel</li>
                    </ul>
                    <br>
                    <p><em>L'équipe FraudGuard</em></p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_content,
                sender=self.app.config.get('MAIL_DEFAULT_SENDER', 'noreply@fraudguard.com')
            )
            
            self.mail.send(msg)
            logger.info(f"Email de bienvenue envoyé à {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email bienvenue: {str(e)}")
            return False