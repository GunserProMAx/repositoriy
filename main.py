
import os
import random
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
            {
                "role": "system",
                "content": "Ты учитель математики. "
                    "Решай квадратные уравнения пошагово. "
                    "Если пользователь указал метод (Виета, дискриминант или другой) — используй его. "
                    "Если нет — решай через дискриминант. "
                    "Объясняй просто и понятно, как в учебнике."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return res.choices[0].message.content

def check_ai(task, answer):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Проверь решение квадратного уравнения. Скажи правильно или нет и покажи правильный ответ."
            },
            {
                "role": "user",
                "content": f"Уравнение: {task}\nОтвет пользователя: {answer}"
            }
        ]
    )
    return res.choices[0].message.content

# =====================
# 🎯 ГЕНЕРАЦИЯ
# =====================
def generate_task():
    x1 = random.randint(-5,5)
    x2 = random.randint(-5,5)
    a = random.choice([1,2,3])

    b = -(x1+x2)*a
    c = x1*x2*a

    return f"{a}x^2 + {b}x + {c} = 0"

# =====================
# 📋 МЕНЮ
# =====================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Решить уравнение", callback_data="solve")],
        [InlineKeyboardButton("🎯 Тренировка", callback_data="train")]
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

    if query.data == "solve":
        context.user_data["mode"] = "solve"
        await query.message.reply_text(
            "✏️ Введи задание/n/n"
            "Например:/n"
            "Реши x^2-5x+6 через теорему Виета"
        )

    elif query.data == "train":
        context.user_data["mode"] = "train"
        task = generate_task()
        context.user_data["task"] = task

        await query.message.reply_text(
            f"🎯 Реши уравнение:\n{task}\n\nВведи корни через запятую"
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
        await update.message.reply_text("🔙 Возврат в меню", reply_markup=menu())

    # ===== ТРЕНИРОВКА =====
    elif mode == "train":
        task = context.user_data.get("task")

        result = check_ai(task, text)

        await update.message.reply_text(result)

        # новое задание
        new_task = generate_task()
        context.user_data["task"] = new_task

        await update.message.reply_text(
            f"🎯 Новое задание:\n{new_task}\n\nВведи корни"
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
app.run_polling()
