import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

# PEGA AS VARIÁVEIS DO RENDER
BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ESTADOS DA CONVERSA
NOME, EMAIL, CONFIRMAR = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Qual é o seu nome?")
    return NOME

async def nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nome'] = update.message.text
    await update.message.reply_text("Perfeito! Agora me diga seu melhor email:")
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Sim, enviar", callback_data='sim')],
        [InlineKeyboardButton("Não, corrigir", callback_data='nao')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Confirma os dados?\n\nNome: {context.user_data['nome']}\nEmail: {context.user_data['email']}",
        reply_markup=
