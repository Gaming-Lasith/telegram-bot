import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# Securely load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Your Telegram user ID (get it from @userinfobot)
ADMIN_ID = 5179577776  # Replace with your real Telegram user ID

# File to store user IDs
USERS_FILE = "users.txt"

# Save a user ID to the file if it's new
def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            pass
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text("👋 Hello! You're now using the bot.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Available commands:\n/start\n/help\n/stats\n/broadcast <message>")

# /stats (admin only)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access denied.")
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    await update.message.reply_text(f"📊 Total users: {len(users)}")

# /broadcast <message> (admin only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access denied.")
    
    if context.args:
        message = " ".join(context.args)
        sent = 0
        failed = 0

        with open(USERS_FILE, "r") as f:
            user_ids = f.read().splitlines()

        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text=message)
                sent += 1
            except:
                failed += 1

        await update.message.reply_text(f"📢 Broadcast complete.\n✅ Sent: {sent}\n❌ Failed: {failed}")
    else:
        await update.message.reply_text("⚠️ Usage: /broadcast <your message>")

# Echo handler for all other messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text(f"You said: {update.message.text}")

# Main setup
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ Bot is running...")
    app.run_polling()
