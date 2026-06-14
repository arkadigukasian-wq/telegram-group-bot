import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# ---------------- DB ----------------
conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS warns (
    user_id INTEGER PRIMARY KEY,
    count INTEGER
)
""")
conn.commit()


def add_warn(user_id):
    cur.execute("SELECT count FROM warns WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute("INSERT INTO warns VALUES (?, ?)", (user_id, 1))
        conn.commit()
        return 1
    else:
        count = row[0] + 1
        cur.execute("UPDATE warns SET count=? WHERE user_id=?", (count, user_id))
        conn.commit()
        return count


def get_warn(user_id):
    cur.execute("SELECT count FROM warns WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else 0


# ---------------- RULES ----------------
RULES_TEXT = """
📜 ПРАВИЛА ГРУППЫ 🇦🇲🤝🇫🇷

• Уважайте всех участников
• Запрещён спам
• Без оскорблений
• Без провокаций

⚠️ 2 предупреждения = бан
"""


# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я бот группы 🇦🇲🤝🇫🇷")


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES_TEXT)


async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is None:
        await update.message.reply_text("Ответь на сообщение пользователя")
        return

    user = update.message.reply_to_message.from_user
    count = add_warn(user.id)

    if count >= 2:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"{user.first_name} забанен ❌")
    else:
        await update.message.reply_text(f"Предупреждение {count}/2 ⚠️")


# ---------------- WELCOME ----------------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member

    if member.new_chat_member.status == "member":
        user = member.new_chat_member.user

        await context.bot.send_message(
            update.effective_chat.id,
            f"Добро пожаловать {user.first_name} 🇦🇲🤝🇫🇷\nНапиши /rules"
        )


# ---------------- DAILY RULES ----------------
async def send_rules(app):
    chat_id = -1001234567890  # ❗ ПОТОМ ЗАМЕНИМ НА ТВОЙ ID

    await app.bot.send_message(chat_id, RULES_TEXT)


# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(ChatMemberHandler(welcome))

    app.run_polling()


if name == "__main__":
    main()
