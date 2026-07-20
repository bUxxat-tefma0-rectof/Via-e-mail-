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
    ] # <-- Colchete fechando aqui, era isso que faltava
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Confirma os dados?\n\nNome: {context.user_data['nome']}\nEmail: {context.user_data['email']}",
        reply_markup=reply_markup
    )
    return CONFIRMAR

async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'sim':
        await query.edit_message_text("Enviando email... Aguarde ⏳")
        try:
            await enviar_email(context.user_data['nome'], context.user_data['email'])
            await query.message.reply_text("Email enviado com sucesso! ✅")
        except Exception as e:
            await query.message.reply_text(f"Deu erro ao enviar: {e}")
    else:
        await query.edit_message_text("Ok, vamos começar de novo. Qual é o seu nome?")
        return NOME
    
    return ConversationHandler.END

async def enviar_email(nome, destinatario):
    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_USER
    msg['To'] = destinatario
    msg['Subject'] = "Bem-vindo!"
    
    html = f"""
    <html>
      <body>
        <h2>Olá {nome}!</h2>
        <p>Seu cadastro foi realizado com sucesso.</p>
        <img src="cid:logo">
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    # ABRE O LOGO - SE FOR .HEIC TROCA AQUI
    with open('logo.png', 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<logo>')
        msg.attach(img)
    
    # ENVIA PELO GMAIL
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()

def main():
    if not BOT_TOKEN:
        print("ERRO: BOT_TOKEN não encontrado nas variáveis de ambiente")
        return
        
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nome)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            CONFIRMAR: [CallbackQueryHandler(confirmar)]
        },
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    print("Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
