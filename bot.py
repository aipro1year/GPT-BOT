from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import sqlite3
import time
from openai import OpenAI

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# DB setup
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages(user_id INTEGER, text TEXT, ts REAL)')
conn.commit()

# anti spam
last_msg = {}
SPAM_DELAY = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("ℹ️ Help", callback_data='help'), InlineKeyboardButton("👑 Admin", callback_data='admin')],
        [InlineKeyboardButton("🤖 About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎉 Welcome {user}!\n\n🤖 Pro GPT-BOT Active 🚀",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/start /help /about /ping /admin /broadcast /chat')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 Pro GPT-BOT v4\nAI Enabled Version')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🟢 Online')

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ No access')
        return
    await update.message.reply_text('👑 Admin Panel\n/broadcast <msg>')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = ' '.join(context.args)
    await update.message.reply_text(f'📢 Broadcast sent: {msg}')

async def chat_with_ai(text: str):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return "⚠️ AI Error, fallback mode active"

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    now = time.time()
    if user_id in last_msg and now - last_msg[user_id] < SPAM_DELAY:
        return
    last_msg[user_id] = now

    cursor.execute('INSERT INTO messages VALUES (?, ?, ?)', (user_id, text, now))
    conn.commit()

    if OPENAI_KEY:
        reply = await chat_with_ai(text)
    else:
        reply = text

    await update.message.reply_text(reply)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('about', about))
app.add_handler(CommandHandler('ping', ping))
app.add_handler(CommandHandler('admin', admin))
app.add_handler(CommandHandler('broadcast', broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print('🚀 AI PRO GPT-BOT RUNNING')
app.run_polling()