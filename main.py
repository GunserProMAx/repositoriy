
import re
import random
import cmath
import numpy as np
import matplotlib.pyplot as plt

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8226591826:AAGefyhkN9aeFd8KNiyDaLBkVtsDbKwQNPY"

# =====================
# 🎨 Формат уравнения
# =====================
def format_eq(a,b,c):
    def s(n):
        return f"+ {n}" if n > 0 else f"- {abs(n)}"

    eq = ""

    if a == 1:
        eq += "x² "
    elif a == -1:
        eq += "-x² "
    else:
        eq += f"{a}x² "

    if b != 0:
        eq += f"{s(b)}x "

    if c != 0:
        eq += f"{s(c)} "

    return eq + "= 0"

# =====================
# 🧠 PARSE (a,b,c)
# =====================
def parse_input(text):
    parts = text.replace(" ", "").split(",")

    if len(parts) != 3:
        raise ValueError

    a = float(parts[0])
    b = float(parts[1])
    c = float(parts[2])

    if a == 0:
        raise ValueError

    return a,b,c

# =====================
# 📘 SOLVE
# =====================
def solve(a,b,c):
    D = b*b - 4*a*c
    x1 = (-b + cmath.sqrt(D))/(2*a)
    x2 = (-b - cmath.sqrt(D))/(2*a)
    return D,x1,x2

def fmt(x):
    if abs(x.imag)<1e-10:
        return round(x.real,2)
    return complex(round(x.real,2), round(x.imag,2))

# =====================
# 🧠 Дискриминант
# =====================
def disc(a,b,c,D,x1,x2):
    return f"""
📘 ДИСКРИМИНАНТ

{format_eq(a,b,c)}

D = {b}² - 4·{a}·{c}
D = {round(D,2)}

x₁ = {fmt(x1)}
x₂ = {fmt(x2)}
"""

# =====================
# 🧠 Виета
# =====================
def vieta(a,b,c,x1,x2):
    if abs(x1.imag)<1e-10:
        return f"""
🧠 ВИЕТА

{format_eq(a,b,c)}

x₁ + x₂ = {round(-b/a,2)}
x₁ · x₂ = {round(c/a,2)}

x₁ = {fmt(x1)}
x₂ = {fmt(x2)}
"""
    return "❌ Виета не применима"

# =====================
# 📊 GRAPH
# =====================
def graph(a,b,c):
    x = np.linspace(-10,10,400)
    y = a*x**2 + b*x + c

    plt.figure()
    plt.grid()
    plt.axhline(0)
    plt.axvline(0)
    plt.plot(x,y)

    file="graph.png"
    plt.savefig(file)
    plt.close()
    return file

# =====================
# 🎯 Тренировка
# =====================
def generate_task():
    a = random.randint(-3,3)
    if a == 0:
        a = 1

    x1 = random.randint(-5,5)
    x2 = random.randint(-5,5)

    b = -(x1 + x2) * a
    c = x1 * x2 * a

    return format_eq(a,b,c), a,b,c,x1,x2

# =====================
# 🎛 МЕНЮ
# =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Ввести коэффициенты",callback_data="input")],
        [InlineKeyboardButton("🎯 Тренировка",callback_data="train")]
    ])

def solve_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Дискриминант",callback_data="disc")],
        [InlineKeyboardButton("🧠 Виета",callback_data="vieta")],
        [InlineKeyboardButton("📊 График",callback_data="graph")],
        [InlineKeyboardButton("🏠 Меню",callback_data="menu")]
    ])

def train_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Ответ",callback_data="tans")],
        [InlineKeyboardButton("🔁 Новое",callback_data="new")],
        [InlineKeyboardButton("🏠 Меню",callback_data="menu")]
    ])

# =====================
# 🏠 START
# =====================
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Привет!\n\nЯ бот, решающий квадратные уравнения 📘",
        reply_markup=main_menu()
    )

# =====================
# 🧠 INPUT
# =====================
async def handle(update:Update, context:ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    try:
        a,b,c = parse_input(text)
        D,x1,x2 = solve(a,b,c)

        context.user_data["data"]=(a,b,c,D,x1,x2)

        await update.message.reply_text(
            f"📘 Уравнение:\n{format_eq(a,b,c)}",
            reply_markup=solve_menu()
        )

    except:
        await update.message.reply_text(
            "⚠️ Неверный ввод\n\nПример:\n1, -5, 6"
        )

# =====================
# 🎯 CALLBACK
# =====================
async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "menu":
        await q.message.reply_text("🏠 Меню", reply_markup=main_menu())
        return

    if q.data == "input":
        await q.message.reply_text(
            "✍️ Введи коэффициенты a, b, c через запятую\n\n"
            "Пример:\n1, -5, 6"
        )
        return

    # TRAIN
    if q.data == "train":
        eq,a,b,c,x1,x2 = generate_task()
        context.user_data["train"] = (a,b,c,x1,x2)

        await q.message.reply_text(f"🎯 Реши:\n{eq}", reply_markup=train_menu())
        return

    if q.data == "new":
        eq,a,b,c,x1,x2 = generate_task()
        context.user_data["train"] = (a,b,c,x1,x2)

        await q.message.reply_text(f"🎯 Новое:\n{eq}", reply_markup=train_menu())
        return

    if q.data == "tans":
        a,b,c,x1,x2 = context.user_data["train"]
        await q.message.reply_text(f"⚡ x₁={x1}, x₂={x2}")
        return

    # SOLVE
    a,b,c,D,x1,x2 = context.user_data.get("data",(0,0,0,0,0,0))

    if q.data == "disc":
        await q.message.reply_text(disc(a,b,c,D,x1,x2))

    elif q.data == "vieta":
        await q.message.reply_text(vieta(a,b,c,x1,x2))

    elif q.data == "graph":
        img = graph(a,b,c)
        await q.message.reply_photo(photo=open(img,"rb"))

# =====================
# ▶️ RUN
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(button))

print("🔥 BOT READY")
app.run_polling()
