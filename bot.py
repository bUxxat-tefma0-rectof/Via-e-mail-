import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

NOME, EMAIL, CPF, TELEFONE = range(4)
TOKEN = os.getenv("TELEGRAM_TOKEN")
EMAIL_USER = os.getenv("EMAIL_USER") # seu gmail
EMAIL_PASS = os.getenv("EMAIL_PASS") # senha de app do gmail

async def start(update: Update, context):
    await update.message.reply_text("Oi! Vou gerar seu extrato 😊\nQual seu nome completo?")
    return NOME

async def nome(update: Update, context):
    context.user_data['nome'] = update.message.text
    await update.message.reply_text("Perfeito. Agora me diga seu email:")
    return EMAIL

async def email(update: Update, context):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Qual seu CPF?")
    return CPF

async def cpf(update: Update, context):
    context.user_data['cpf'] = update.message.text
    await update.message.reply_text("E seu telefone?")
    return TELEFONE

async def telefone(update: Update, context):
    context.user_data['telefone'] = update.message.text
    
    # Gera e envia o email
    enviar_email(context.user_data)
    
    await update.message.reply_text(f"Pronto! Enviei o extrato para {context.user_data['email']} 📧")
    return ConversationHandler.END

def enviar_email(dados):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = dados['email']
    msg['Subject'] = "Seu Extrato"
    
    # Corpo do email com HTML e logo
    html = f"""
    <html>
    <body>
        <img src="cid:logo" width="150"><br>
        <h2>Extrato de Cadastro</h2>
        <p><b>Nome:</b> {dados['nome']}</p>
        <p><b>CPF:</b> {dados['cpf']}</p>
        <p><b>Telefone:</b> {dados['telefone']}</p>
        <p><b>Email:</b> {dados['email']}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    # Anexa logo.png
    with open('logo.png', 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<logo>')
        msg.attach(img)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()

app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NOME: [MessageHandler(filters.TEXT, nome)],
        EMAIL: [MessageHandler(filters.TEXT, email)],
        CPF: [MessageHandler(filters.TEXT, cpf)],
        TELEFONE: [MessageHandler(filters.TEXT, telefone)],
    },
    fallbacks=[]
)
app.add_handler(conv)
app.run_polling()
