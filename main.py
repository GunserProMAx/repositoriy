
import os
from openai import OpenAI

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# =====================
# 🔑 КЛЮЧИ
# =====================
TELEGRAM_TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================
# 🧠 GPT ФУНКЦИЯ
# =====================
def ask_gpt(user_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты учитель математики. "
                    "Решай квадратные уравнения пошагово. "
                    "Если пользователь указал метод (Виета, дискриминант или другой) — используй его. "
                    "Если нет — решай через дискриминант. "
                    "Пиши понятно и красиво, как в учебнике."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )

    return response.choices[0].message.content

# =====================
# 🏠 START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Я умный бот по квадратным уравнениям 🤖\n\n"
        "Напиши:\n"
        "Реши x^2 - 5x + 6 через теорему Виета"
    )

# =====================
# 🧠 HANDLE
# =====================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        answer = ask_gpt(user_text)
        await update.message.reply_text(answer)

    except Exception as e:
        print("GPT ERROR:", e)
        await update.message.reply_text(f"⚠️ Ошибка GPT:\n{e}")

# =====================
# ▶️ ЗАПУСК
# =====================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("🔥 GPT BOT RUNNING")
app.run_polling()
