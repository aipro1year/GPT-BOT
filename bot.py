from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import os
import sqlite3
import time
from openai import OpenAI
import random

BOT_NAMES = [
    "🤖 GPT Nexus Bot",
    "⚡ Alpha AI Bot",
    "🚀 UltraGPT Assistant",
    "🧠 Neo AI Chat Bot",
    "💎 Pro AI Assistant"
]

def get_bot_name():
    return random.choice(BOT_NAMES)

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages(user_id INTEGER, text TEXT, ts REAL)')
cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, first_name TEXT, last_seen REAL)')
conn.commit()

last_msg = {}
SPAM_DELAY = 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = get_bot_name()

    cursor.execute('INSERT OR REPLACE INTO users VALUES (?, ?, ?)', (user.id, user.first_name, time.time()))
    conn.commit()

    keyboard = [
        [InlineKeyboardButton("ℹ️ Help", callback_data='help'), InlineKeyboardButton("👑 Admin", callback_data='admin')],
        [InlineKeyboardButton("🤖 About", callback_data='about'), InlineKeyboardButton("💬 Chat", callback_data='chat')]
    ]

    await update.message.reply_text(
        f"🎉 Welcome {user.first_name}!\n\n🚀 {bot_name} Active Now",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await query.edit_message_text('/start /help /about /ping /admin /stats /broadcast /chat')

    elif query.data == 'admin':
        if query.from_user.id != ADMIN_ID:
            await query.edit_message_text('❌ No access')
        else:
            await query.edit_message_text('👑 Admin Panel\n/stats /broadcast')

    elif query.data == 'about':
        await query.edit_message_text('🤖 Multi-Brand AI Bot System')

    elif query.data == 'chat':
        await query.edit_message_text('💬 Send any message to chat with AI 🤖')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('/start /help /about /ping /admin /stats /broadcast /chat')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 Multi-Brand AI Bot System')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🟢 Online')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ No access')
        return

    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM messages')
    msgs = cursor.fetchone()[0]

    await update.message.reply_text(f'📊 Users: {users}\n💬 Messages: {msgs}')

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('❌ No access')
        return
    await update.message.reply_text('👑 Admin Panel\n/stats')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = ' '.join(context.args)
    await update.message.reply_text(f'📢 Broadcast: {msg}')

async def chat_with_ai(text: str):
    if not client:
        return "🤖 AI not configured"

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}]
        )
        return res.choices[0].message.content
    except:
        return "⚠️ AI error"

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    now = time.time()
    if user.id in last_msg and now - last_msg[user.id] < SPAM_DELAY:
        return
    last_msg[user.id] = now

    cursor.execute('INSERT INTO messages VALUES (?, ?, ?)', (user.id, text, now))
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?, ?, ?)', (user.id, user.first_name, now))
    conn.commit()

    reply = await chat_with_ai(text) if client else text
    await update.message.reply_text(reply)

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('about', about))
app.add_handler(CommandHandler('ping', ping))
app.add_handler(CommandHandler('stats', stats))
app.add_handler(CommandHandler('admin', admin))
app.add_handler(CommandHandler('broadcast', broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(CallbackQueryHandler(callback_handler))

print('🚀 MULTI-BRAND BOT RUNNING')
app.run_polling()