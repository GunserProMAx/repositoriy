
import random
import cmath
import numpy as np
import matplotlib.pyplot as plt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, Filters, ContextTypes

TOKEN = "8226591826:AAGefyhkN9aeFd8KNiyDaLBkVtsDbKwQNPY"

# =====================
# 📊 СТАТИСТИКА
# =====================
def init_user(context):
    if "stats" not in context.user_data:
        context.user_data["stats"] = {
            "solved": 0,
            "train": 0,
            "correct": 0
        }

# =====================
# 🎨 ФОРМАТ
# =====================
def format_eq(a,b,c):
    def s(n): return f"+ {n}" if n>0 else f"- {abs(n)}"
    eq = f"{a}x² " if a not in [1,-1] else ("x² " if a==1 else "-x² ")
    if b: eq += f"{s(b)}x "
    if c: eq += f"{s(c)} "
    return eq + "= 0"

# =====================
# 🧠 SOLVE
# =====================
def solve(a,b,c):
    D = b*b - 4*a*c
    x1 = (-b + cmath.sqrt(D))/(2*a)
    x2 = (-b - cmath.sqrt(D))/(2*a)
    return x1,x2

# =====================
# 🎯 ГЕНЕРАЦИЯ
# =====================
def gen_task():
    a = random.choice([-3,-2,-1,1,2,3])
    x1 = random.randint(-5,5)
    x2 = random.randint(-5,5)
    b = -(x1+x2)*a
    c = x1*x2*a
    return a,b,c,x1,x2

# =====================
# 🎛 МЕНЮ
# =====================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Ввести коэффициенты",callback_data="input")],
        [InlineKeyboardButton("🎯 Тренировка",callback_data="train")],
        [InlineKeyboardButton("🎓 Экзамен",callback_data="exam")],
        [InlineKeyboardButton("📊 Статистика",callback_data="stats")]
    ])

# =====================
# 🏠 START
# =====================
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    init_user(context)

    await update.message.reply_text(
        "👋 Привет!\n\nЯ бот, решающий квадратные уравнения 📘",
        reply_markup=menu()
    )

# =====================
# 📊 СТАТИСТИКА
# =====================
async def show_stats(update, context):
    s = context.user_data["stats"]

    await update.callback_query.message.reply_text(
        f"""
📊 Статистика

Решено: {s['solved']}
Тренировок: {s['train']}
Правильно: {s['correct']}
"""
    )

# =====================
# 🎯 CALLBACK
# =====================
async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    init_user(context)

    # ===== MENU =====
    if q.data == "input":
        await q.message.reply_text("Введи: a, b, c\nПример: 1, -5, 6")
        return

    if q.data == "stats":
        await show_stats(update, context)
        return

    # ===== TRAIN =====
    if q.data == "train":
        a,b,c,x1,x2 = gen_task()
        context.user_data["train"]=(a,b,c,x1,x2)

        await q.message.reply_text(f"🎯 {format_eq(a,b,c)}")
        return

    # ===== EXAM =====
    if q.data == "exam":
        context.user_data["exam"] = {
            "q": 0,
            "score": 0
        }
        await next_exam(q.message, context)
        return

# =====================
# 🎓 ЭКЗАМЕН
# =====================
async def next_exam(msg, context):
    exam = context.user_data["exam"]

    if exam["q"] >= 5:
        await msg.reply_text(
            f"🏁 Экзамен завершён!\nРезультат: {exam['score']}/5"
        )
        return

    a,b,c,x1,x2 = gen_task()
    context.user_data["exam_task"] = (x1,x2)

    exam["q"] += 1

    await msg.reply_text(
        f"🎓 Задание {exam['q']}:\n{format_eq(a,b,c)}\n\n"
        "Введи корни через запятую"
    )

# =====================
# 🧠 HANDLE TEXT
# =====================
async def handle(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    init_user(context)

    # ===== ЭКЗАМЕН =====
    if "exam" in context.user_data:
        try:
            user = [float(x) for x in text.split(",")]
            x1,x2 = context.user_data["exam_task"]

            if set([round(x1,2), round(x2,2)]) == set([round(user[0],2), round(user[1],2)]):
context.user_data["exam"]["score"] += 1
                context.user_data["stats"]["correct"] += 1

            await next_exam(update.message, context)
            return
        except:
            await update.message.reply_text("Ошибка ввода")
            return

    # ===== ОБЫЧНЫЙ РЕЖИМ =====
    try:
        a,b,c = [float(x) for x in text.split(",")]
        x1,x2 = solve(a,b,c)

        context.user_data["stats"]["solved"] += 1

        await update.message.reply_text(
            f"Ответ: {round(x1.real,2)}, {round(x2.real,2)}"
        )
    except:
        await update.message.reply_text("Ошибка ввода")
