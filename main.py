
import os
from groq import Groq

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

# =====================
# 🔑 КЛЮЧИ
# =====================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# =====================
# 🧠 AI ФУНКЦИИ
# =====================
def solve_ai(text):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Ты учитель математики. Решай квадратные уравнения пошагово."},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content

def check_ai(task, answer):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Проверь решение квадратного уравнения. Скажи правильно или нет и покажи решение."},
            {"role": "user", "content": f"Уравнение: {task}\nОтвет: {answer}"}
        ]
    )
    return res.choices[0].message.content

def generate_ai_task():
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Сгенерируй квадратное уравнение с целыми корнями. Только уравнение без объяснений."
            }
        ]
    )
    return res.choices[0].message.content

# =====================
# 📋 МЕНЮ
# =====================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Решить уравнение", callback_data="solve")],
        [InlineKeyboardButton("🎯 Тренировка", callback_data="train")]
    ])

def train_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Продолжить", callback_data="next_train")],
        [InlineKeyboardButton("🔙 В меню", callback_data="menu")]
    ])

# =====================
# 🏠 START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "👋 Я бот по квадратным уравнениям 🤖",
        reply_markup=menu()
    )

# =====================
# 🎛 КНОПКИ
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ===== В МЕНЮ =====
    if query.data == "menu":
        context.user_data.clear()
        await query.message.reply_text("📋 Меню", reply_markup=menu())

    # ===== РЕШЕНИЕ =====
    elif query.data == "solve":
        context.user_data["mode"] = "solve"

        await query.message.reply_text(
            "✏️ Введи уравнение\n\n"
            "Пример:\n"
            "Реши x^2 - 5x + 6 через теорему Виета"
        )

    # ===== ТРЕНИРОВКА =====
    elif query.data == "train":
        context.user_data["mode"] = "train"

        task = generate_ai_task()
        context.user_data["task"] = task

        await query.message.reply_text(
            f"🎯 Реши уравнение:\n{task}\n\nВведи корни через запятую"
        )

    elif query.data == "next_train":
        task = generate_ai_task()
        context.user_data["task"] = task

        await query.message.reply_text(
            f"🎯 Новое задание:\n{task}\n\nВведи корни"
        )

# =====================
# 🧠 HANDLE
# =====================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mode = context.user_data.get("mode")

    # ===== РЕШЕНИЕ =====
    if mode == "solve":
        answer = solve_ai(text)

        await update.message.reply_text(answer)
        await update.message.reply_text("🔙 В меню", reply_markup=menu())

    # ===== ТРЕНИРОВКА =====
    elif mode == "train":
        task = context.user_data.get("task")

        result = check_ai(task, text)

        await update.message.reply_text(result)
        await update.message.reply_text(
            "Что дальше?",
            reply


in_menu()
        )

    else:
        await update.message.reply_text("Выбери режим", reply_markup=menu())

# =====================
# ▶️ ЗАПУСК
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("🔥 BOT RUNNING")
app.run_polling()_markup=tra
