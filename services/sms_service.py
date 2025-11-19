import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self, app):
        self.app = app
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialise le client Twilio (simulation pour le développement)"""
        try:
            # Pour le développement, on simule Twilio
            account_sid = self.app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = self.app.config.get('TWILIO_AUTH_TOKEN')
            
            if account_sid and auth_token:
                # En production, on utiliserait:
                # from twilio.rest import Client
                # self.client = Client(account_sid, auth_token)
                logger.info("Service SMS initialisé (mode simulation)")
            else:
                logger.warning("Configuration SMS manquante - mode simulation activé")
                
        except Exception as e:
            logger.error(f"Erreur initialisation SMS: {str(e)}")
    
    def send_alert(self, phone_number, message):
        """Envoie une alerte par SMS (simulation)"""
        try:
            # Simulation d'envoi SMS pour le développement
            logger.info(f"[SIMULATION SMS] Envoyé à {phone_number}: 🚨 Alerte Fraude: {message}")
            
            # En production, décommentez ce code:
            """
            if not self.client:
                logger.warning("Client SMS non initialisé")
                return False
            
            twilio_phone = self.app.config.get('TWILIO_PHONE_NUMBER')
            
            message = self.client.messages.create(
                body=f"🚨 Alerte Fraude: {message}",
                from_=twilio_phone,
                to=phone_number
            )
            
            logger.info(f"SMS envoyé à {phone_number}: {message.sid}")
            """
            
            return True  # Simulation réussie
            
        except Exception as e:
            logger.error(f"Erreur envoi SMS: {str(e)}")
            return False
    
    def send_verification_code(self, phone_number, code):
        """Envoie un code de vérification (simulation)"""
        try:
            # Simulation d'envoi de code
            logger.info(f"[SIMULATION SMS] Code de vérification envoyé à {phone_number}: {code}")
            
            # En production:
            """
            if not self.client:
                return False
            
            twilio_phone = self.app.config.get('TWILIO_PHONE_NUMBER')
            
            message = self.client.messages.create(
                body=f"Votre code de vérification FraudGuard: {code}",
                from_=twilio_phone,
                to=phone_number
            )
            """
            
            logger.info(f"Code vérification envoyé à {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi code vérification: {str(e)}")
            return False