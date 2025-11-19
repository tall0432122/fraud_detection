import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_pdf_report(self, user_id, user, predictions):
        """Génère un rapport PDF détaillé (simulation)"""
        try:
            # Simulation de génération PDF
            # En production, vous utiliseriez reportlab ou autre bibliothèque PDF
            
            filename = f"{self.reports_dir}/report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Créer un fichier PDF simulé
            with open(filename, 'w') as f:
                f.write(f"Rapport FraudGuard - {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Utilisateur: {user.username}\n")
                f.write(f"Email: {user.email}\n")
                f.write(f"Date du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                # Statistiques
                total_pred = len(predictions)
                fraud_pred = len([p for p in predictions if p.prediction == 'Fraude'])
                safe_pred = total_pred - fraud_pred
                fraud_rate = (fraud_pred / total_pred * 100) if total_pred > 0 else 0
                
                f.write("STATISTIQUES:\n")
                f.write(f"Total des prédictions: {total_pred}\n")
                f.write(f"Transactions sûres: {safe_pred}\n")
                f.write(f"Fraudes détectées: {fraud_pred}\n")
                f.write(f"Taux de fraude: {fraud_rate:.2f}%\n\n")
                
                # Dernières prédictions
                f.write("DERNIÈRES PRÉDICTIONS:\n")
                for pred in predictions[:10]:
                    f.write(f"- {pred.created_at.strftime('%Y-%m-%d')}: {pred.prediction} "
                           f"(Confiance: {pred.confidence*100:.1f}%, "
                           f"Montant: {pred.amount or 0:.2f} {pred.currency})\n")
            
            logger.info(f"Rapport PDF généré: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erreur génération PDF: {str(e)}")
            raise
    
    def generate_excel_report(self, user_id, user, predictions):
        """Génère un rapport Excel détaillé"""
        try:
            # Création du DataFrame
            data = []
            for pred in predictions:
                data.append({
                    'Date': pred.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Résultat': pred.prediction,
                    'Confiance': f"{pred.confidence*100:.2f}%",
                    'Montant': pred.amount or 0,
                    'Devise': pred.currency,
                    'Transaction_ID': pred.id
                })
            
            df = pd.DataFrame(data)
            
            # Création du fichier Excel
            filename = f"{self.reports_dir}/report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Onglet des prédictions
                df.to_excel(writer, sheet_name='Prédictions', index=False)
                
                # Onglet des statistiques
                stats_data = {
                    'Métrique': ['Total Prédictions', 'Transactions Sûres', 'Fraudes Détectées', 'Taux de Fraude'],
                    'Valeur': [
                        len(predictions),
                        len([p for p in predictions if p.prediction == 'Non Fraude']),
                        len([p for p in predictions if p.prediction == 'Fraude']),
                        f"{(len([p for p in predictions if p.prediction == 'Fraude']) / len(predictions) * 100) if predictions else 0:.2f}%"
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
                
                # Onglet des analyses mensuelles
                if len(predictions) > 0:
                    fraud_by_month = []
                    for pred in predictions:
                        if pred.prediction == 'Fraude':
                            fraud_by_month.append(pred.created_at.strftime('%Y-%m'))
                    
                    if fraud_by_month:
                        fraud_df = pd.DataFrame({'Mois': fraud_by_month})
                        fraud_count = fraud_df['Mois'].value_counts().reset_index()
                        fraud_count.columns = ['Mois', 'Nombre de Fraudes']
                        fraud_count.to_excel(writer, sheet_name='Analyse Mensuelle', index=False)
            
            logger.info(f"Rapport Excel généré: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erreur génération Excel: {str(e)}")
            raise
    
    def generate_analysis_chart(self, predictions):
        """Génère un graphique d'analyse"""
        try:
            if not predictions:
                return None
            
            # Préparer les données pour le graphique
            dates = [pred.created_at.date() for pred in predictions]
            frauds = [1 if pred.prediction == 'Fraude' else 0 for pred in predictions]
            
            # Créer un graphique simple
            plt.figure(figsize=(10, 6))
            plt.plot(dates, frauds, 'ro-', alpha=0.7)
            plt.title('Évolution des Détections de Fraude')
            plt.xlabel('Date')
            plt.ylabel('Fraude (1=Oui, 0=Non)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Sauvegarder en mémoire
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            # Convertir en base64 pour l'affichage HTML
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Erreur génération graphique: {str(e)}")
            return None