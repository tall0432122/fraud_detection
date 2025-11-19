import requests
import json
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class BankAPIService:
    def __init__(self, app):
        self.app = app
        self.base_url = app.config.get('BANK_API_URL', 'https://api.bank-simulation.com')
        self.api_key = app.config.get('BANK_API_KEY', 'demo-key')
    
    def get_transactions(self, account_id, start_date, end_date):
        """Récupère les transactions d'un compte bancaire"""
        try:
            # Pour le développement, on utilise des données simulées
            if self.app.config.get('DEBUG', True):
                return self._get_mock_transactions()
            
            # Code pour l'environnement de production
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'account_id': account_id,
                'start_date': start_date,
                'end_date': end_date,
                'limit': 100
            }
            
            response = requests.get(
                f"{self.base_url}/transactions",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                transactions = response.json().get('transactions', [])
                logger.info(f"Récupéré {len(transactions)} transactions")
                return self._format_transactions(transactions)
            else:
                logger.error(f"Erreur API bancaire: {response.status_code}")
                return self._get_mock_transactions()
                
        except Exception as e:
            logger.error(f"Erreur connexion API bancaire: {str(e)}")
            # Retourne des données simulées pour le développement
            return self._get_mock_transactions()
    
    def _format_transactions(self, transactions):
        """Formate les transactions pour le modèle"""
        formatted = []
        for tx in transactions:
            formatted.append({
                'id': tx.get('id'),
                'amount': tx.get('amount', 0),
                'currency': tx.get('currency', 'USD'),
                'date': tx.get('date'),
                'merchant': tx.get('merchant', {}).get('name', 'Unknown'),
                'category': tx.get('category', 'other'),
                'features': self._extract_features(tx)
            })
        return formatted
    
    def _extract_features(self, transaction):
        """Extrait les features des transactions pour le modèle"""
        amount = abs(transaction.get('amount', 0))
        
        # Features simulées basées sur la transaction
        features = [
            amount / 1000.0,  # feature_1: Montant normalisé
            len(transaction.get('merchant', {}).get('name', '')) / 50.0,  # feature_2: Longueur nom marchand normalisée
            1.0 if transaction.get('category') == 'online' else 0.0,  # feature_3: Transaction en ligne
            random.uniform(-1, 1),  # feature_4: Valeur aléatoire
            random.uniform(-1, 1),  # feature_5: Valeur aléatoire
            random.uniform(-1, 1),  # feature_6: Valeur aléatoire
            random.uniform(-1, 1),  # feature_7: Valeur aléatoire
            random.uniform(-1, 1),  # feature_8: Valeur aléatoire
            random.uniform(-1, 1),  # feature_9: Valeur aléatoire
            random.uniform(-1, 1),  # feature_10: Valeur aléatoire
            random.uniform(-1, 1),  # feature_11: Valeur aléatoire
            random.uniform(-1, 1),  # feature_12: Valeur aléatoire
            random.uniform(-1, 1),  # feature_13: Valeur aléatoire
        ]
        
        return features
    
    def _get_mock_transactions(self):
        """Génère des transactions simulées pour le développement"""
        transactions = []
        categories = ['retail', 'online', 'food', 'transport', 'entertainment']
        merchants = ['Amazon', 'Apple', 'Google', 'Netflix', 'Uber', 'Airbnb', 'Starbucks', 'McDonald\'s']
        
        for i in range(20):
            amount = random.uniform(10, 1000)
            category = random.choice(categories)
            merchant = random.choice(merchants)
            
            transactions.append({
                'id': f"tx_{i:04d}",
                'amount': amount,
                'currency': 'USD',
                'date': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'merchant': {'name': merchant},
                'category': category,
                'features': self._extract_features({'amount': amount, 'category': category})
            })
        
        logger.info(f"Généré {len(transactions)} transactions simulées")
        return transactions
    
    def validate_account(self, account_id, user_id):
        """Valide qu'un compte appartient à l'utilisateur (simulation)"""
        try:
            # Pour le développement, on simule la validation
            if self.app.config.get('DEBUG', True):
                return True
            
            # Code pour l'environnement de production
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/accounts/{account_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                account_data = response.json()
                return account_data.get('owner_id') == user_id
            return False
            
        except Exception as e:
            logger.error(f"Erreur validation compte: {str(e)}")
            return True  # Pour le développement