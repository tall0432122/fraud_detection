import numpy as np
import logging
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class OnlineLearner:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'model/fraud_model.pkl'
        self.scaler_path = 'model/scaler.pkl'
        self.feedback_data = []
        self.batch_size = 100
        self.load_model()
        
    def load_model(self):
        """Charge le modèle existant ou en crée un nouveau"""
        try:
            os.makedirs('model', exist_ok=True)
            
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Modèle chargé avec succès")
            else:
                self.initialize_model()
                logger.info("Nouveau modèle initialisé")
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {str(e)}")
            self.initialize_model()
    
    def initialize_model(self):
        """Initialise un nouveau modèle"""
        self.model = SGDClassifier(
            loss='log_loss',
            learning_rate='optimal',
            eta0=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Données d'initialisation simulées
        X_initial = np.random.randn(100, 13)
        y_initial = np.random.choice([0, 1], size=100, p=[0.9, 0.1])
        
        self.scaler.fit(X_initial)
        X_scaled = self.scaler.transform(X_initial)
        self.model.partial_fit(X_scaled, y_initial, classes=[0, 1])
        self.save_model()
    
    def partial_fit(self, data):
        """Met à jour le modèle avec de nouvelles données"""
        try:
            features = np.array(data['features'])
            labels = np.array(data['labels'])
            
            if len(features) == 0:
                return
            
            # Adaptation du scaler
            if hasattr(self.scaler, 'n_samples_seen_'):
                self.scaler.partial_fit(features)
            else:
                self.scaler.fit(features)
            
            # Normalisation des features
            features_scaled = self.scaler.transform(features)
            
            # Apprentissage en ligne du modèle
            self.model.partial_fit(features_scaled, labels, classes=[0, 1])
            
            # Sauvegarde du modèle mis à jour
            self.save_model()
            
            logger.info(f"Modèle mis à jour avec {len(features)} nouveaux échantillons")
            
        except Exception as e:
            logger.error(f"Erreur mise à jour modèle: {str(e)}")
    
    def predict(self, features):
        """Fait une prédiction avec le modèle actuel"""
        try:
            features_array = np.array(features).reshape(1, -1)
            
            if hasattr(self.scaler, 'mean_'):
                features_scaled = self.scaler.transform(features_array)
            else:
                features_scaled = features_array
            
            prediction = self.model.predict(features_scaled)[0]
            
            # Pour SGDClassifier avec log_loss, on a predict_proba
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)[0]
            else:
                # Fallback pour les modèles sans predict_proba
                decision = self.model.decision_function(features_scaled)[0]
                probabilities = [1 / (1 + np.exp(-decision)), 1 / (1 + np.exp(decision))]
                probabilities = probabilities / np.sum(probabilities)
            
            return prediction, probabilities
        except Exception as e:
            logger.error(f"Erreur prédiction: {str(e)}")
            return 0, [0.5, 0.5]
    
    def save_model(self):
        """Sauvegarde le modèle et le scaler"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Modèle sauvegardé avec succès")
        except Exception as e:
            logger.error(f"Erreur sauvegarde modèle: {str(e)}")
    
    def get_model_info(self):
        """Retourne les informations du modèle"""
        if hasattr(self.model, 'coef_'):
            return {
                'type': type(self.model).__name__,
                'n_features': len(self.model.coef_[0]) if self.model.coef_ is not None else 0,
                'n_samples': self.model.t_ if hasattr(self.model, 't_') else 0
            }
        return {'type': 'Non initialisé'}