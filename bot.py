from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    msg = f'''🎉 Welcome {user}!

🤖 GPT-BOT Professional Edition

✅ Echo Messages
✅ Admin Panel
✅ Status Monitoring
✅ 24/7 Hosting Ready

📌 Commands
/start
/help
/ping
/about
/admin

Have a great day! 🚀'''
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('📚 Commands:\n/start\n/help\n/ping\n/about\n/admin')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 GPT-BOT\nDeveloper: Mohammad Rifat\nVersion: 2.0')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🟢 Bot Status: Online')

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ Access Denied')
        return
    await update.message.reply_text('👑 Admin Panel\n/stats')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text('📊 System Status: Running')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('about', about))
app.add_handler(CommandHandler('ping', ping))
app.add_handler(CommandHandler('admin', admin))
app.add_handler(CommandHandler('stats', stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print('🚀 GPT-BOT Started')
app.run_polling()