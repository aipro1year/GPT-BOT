from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    welcome_text = f"""👋 Welcome, {user}!\n\n🤖 Welcome to GPT-BOT\n\n✨ Features:\n• Echo Messages\n• Fast Responses\n• Admin Commands\n• 24/7 Online\n\n📌 Available Commands:\n/start - Start Bot\n/help - Help Menu\n/ping - Check Status\n\nEnjoy using the bot! 🚀"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/start\n/help\n/ping\n/admin')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🏓 Pong! Bot is running.')

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ You are not authorized.')
        return
    await update.message.reply_text('👑 Admin Panel\n/stats')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text('📊 Bot Status: Online')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('ping', ping))
app.add_handler(CommandHandler('admin', admin))
app.add_handler(CommandHandler('stats', stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()