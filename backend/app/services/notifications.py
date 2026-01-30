"""
Service de notifications pour alertes de prix
Supporte Email, Telegram et WhatsApp
"""
import os
import logging
from typing import Optional
from datetime import datetime

# Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Telegram
from telegram import Bot
from telegram.error import TelegramError

# WhatsApp (via Twilio)
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class NotificationService:
    """Service centralisé pour envoyer des notifications"""
    
    def __init__(self):
        # Configuration Email
        self.smtp_enabled = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.email_from = os.getenv('EMAIL_FROM', self.smtp_user)
        
        # Configuration Telegram
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_bot = None
        if self.telegram_enabled and self.telegram_token:
            try:
                self.telegram_bot = Bot(token=self.telegram_token)
            except Exception as e:
                logger.error(f"Erreur initialisation Telegram: {e}")
                self.telegram_enabled = False
        
        # Configuration WhatsApp/Twilio
        self.twilio_enabled = os.getenv('TWILIO_ENABLED', 'false').lower() == 'true'
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', '')
        self.twilio_client = None
        if self.twilio_enabled and self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
            except Exception as e:
                logger.error(f"Erreur initialisation Twilio: {e}")
                self.twilio_enabled = False
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """Envoyer un email"""
        if not self.smtp_enabled:
            logger.warning("SMTP désactivé, email non envoyé")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Texte brut
            msg.attach(MIMEText(body, 'plain'))
            
            # HTML si fourni
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email envoyé à {to_email}")
            return True
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    async def send_telegram(
        self, 
        chat_id: str, 
        message: str,
        parse_mode: str = 'HTML'
    ) -> bool:
        """Envoyer un message Telegram"""
        if not self.telegram_enabled or not self.telegram_bot:
            logger.warning("Telegram désactivé, message non envoyé")
            return False
        
        try:
            await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Message Telegram envoyé à {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Erreur Telegram: {e}")
            return False
    
    async def send_whatsapp(
        self, 
        to_number: str, 
        message: str
    ) -> bool:
        """Envoyer un message WhatsApp via Twilio"""
        if not self.twilio_enabled or not self.twilio_client:
            logger.warning("WhatsApp/Twilio désactivé, message non envoyé")
            return False
        
        try:
            # Format du numéro WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=to_number
            )
            logger.info(f"WhatsApp envoyé à {to_number}: {message_obj.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Erreur Twilio: {e}")
            return False
    
    async def send_price_alert(
        self,
        user_email: str,
        user_phone: Optional[str],
        telegram_chat_id: Optional[str],
        product_name: str,
        current_price: float,
        alert_type: str,
        threshold: Optional[float],
        notification_channel: str
    ) -> bool:
        """
        Envoyer une alerte de prix via le canal choisi
        
        Args:
            notification_channel: 'email', 'telegram', 'whatsapp', 'sms'
        """
        # Préparer le message
        if alert_type == 'target_price':
            message = f"🎯 Prix cible atteint!\n\n{product_name}\nPrix actuel: {current_price} FCFA\nSeuil: {threshold} FCFA"
        elif alert_type == 'percentage_drop':
            message = f"📉 Baisse de prix significative!\n\n{product_name}\nPrix actuel: {current_price} FCFA\nBaisse: {threshold}%"
        elif alert_type == 'availability':
            message = f"✅ Produit disponible!\n\n{product_name}\nPrix: {current_price} FCFA"
        else:
            message = f"🔔 Alerte de prix\n\n{product_name}\nPrix: {current_price} FCFA"
        
        # Envoyer selon le canal
        if notification_channel == 'email':
            subject = f"🔔 Alerte Prix: {product_name}"
            html = f"""
            <h2>Alerte de Prix</h2>
            <p><strong>{product_name}</strong></p>
            <p>Prix actuel: <strong>{current_price} FCFA</strong></p>
            <p>Type d'alerte: {alert_type}</p>
            <p>Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            """
            return await self.send_email(user_email, subject, message, html)
        
        elif notification_channel == 'telegram' and telegram_chat_id:
            formatted_message = f"<b>🔔 Alerte de Prix</b>\n\n{message}"
            return await self.send_telegram(telegram_chat_id, formatted_message)
        
        elif notification_channel == 'whatsapp' and user_phone:
            return await self.send_whatsapp(user_phone, message)
        
        else:
            logger.warning(f"Canal non supporté ou info manquante: {notification_channel}")
            return False
    
    async def test_notification(
        self,
        channel: str,
        user_email: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> dict:
        """Test d'envoi de notification"""
        result = {"success": False, "message": ""}
        
        if channel == 'email' and user_email:
            success = await self.send_email(
                user_email,
                "Test Price Tracker",
                "Ceci est un message de test. Vos notifications sont configurées correctement!"
            )
            result["success"] = success
            result["message"] = "Email envoyé" if success else "Échec envoi email"
        
        elif channel == 'telegram' and telegram_chat_id:
            success = await self.send_telegram(
                telegram_chat_id,
                "<b>✅ Test réussi!</b>\n\nVotre bot Telegram est configuré correctement."
            )
            result["success"] = success
            result["message"] = "Telegram envoyé" if success else "Échec envoi Telegram"
        
        elif channel == 'whatsapp' and phone_number:
            success = await self.send_whatsapp(
                phone_number,
                "✅ Test réussi! Votre WhatsApp est configuré correctement pour Price Tracker."
            )
            result["success"] = success
            result["message"] = "WhatsApp envoyé" if success else "Échec envoi WhatsApp"
        
        else:
            result["message"] = "Canal non supporté ou informations manquantes"
        
        return result


# Instance globale
notification_service = NotificationService()
