
import random
import cmath

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8226591826:AAGefyhkN9aeFd8KNiyDaLBkVtsDbKwQNPY"

# =====================
# 📊 СТАТИСТИКА
# =====================
def init_user(context):
    if "stats" not in context.user_data:
        context.user_data["stats"] = {
            "solved": 0,
            "correct": 0
        }

# =====================
# 🎨 УРАВНЕНИЕ
# =====================
def format_eq(a,b,c):
    def s(n): return f"+ {n}" if n>0 else f"- {abs(n)}"
    eq = f"{a}x² " if a not in [1,-1] else ("x² " if a==1 else "-x² ")
    if b: eq += f"{s(b)}x "
    if c: eq += f"{s(c)} "
    return eq + "= 0"

# =====================
# 🧠 РЕШЕНИЕ
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
    a = random.choice([-10,-9,-8.-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8,9,10])
    x1 = random.randint(-10,10)
    x2 = random.randint(--10,10)
    b = -(x1+x2)*a
    c = x1*x2*a
    return a,b,c,x1,x2

# =====================
# 🎛 МЕНЮ
# =====================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Ввести коэффициенты",callback_data="input")],
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
        "👋 Привет!\nЯ бот для квадратных уравнений",
        reply_markup=menu()
    )

# =====================
# 📊 СТАТИСТИКА
# =====================
async def show_stats(update, context):
    s = context.user_data["stats"]

    await update.callback_query.message.reply_text(
        f"📊 Решено: {s['solved']}\nПравильно: {s['correct']}"
    )

# =====================
# 🎓 ЭКЗАМЕН
# =====================
async def next_exam(msg, context):
    exam = context.user_data["exam"]

    if exam["q"] >= 5:
        await msg.reply_text(f"🏁 Результат: {exam['score']}/5")
        context.user_data.pop("exam")
        return

    a,b,c,x1,x2 = gen_task()
    context.user_data["exam_task"] = (x1,x2)

    exam["q"] += 1

    await msg.reply_text(
        f"🎓 Задание {exam['q']}:\n{format_eq(a,b,c)}\n\nВведи корни через запятую"
    )

# =====================
# 🎛 КНОПКИ
# =====================
async def button(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    init_user(context)

    if q.data == "input":
        await q.message.reply_text("Введи: a, b, c\nПример: 1, -5, 6")

    elif q.data == "stats":
        await show_stats(update, context)

    elif q.data == "exam":
        context.user_data["exam"] = {"q":0,"score":0}
        await next_exam(q.message, context)

# =====================
# 🧠 ВВОД
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
        except:
            await update.message.reply_text("Ошибка ввода")
        return

    # ===== ОБЫЧНЫЙ =====
    try:
        a,b,c = [float(x) for x in text.split(",")]
        x1,x2 = solve(a,b,c)

        context.user_data["stats"]["solved"] += 1

        await update.message.reply_text(
            f"Ответ: {round(x1.real,2)}, {round(x2.real,2)}"
        )
    except:
        await update.message.reply_text("Ошибка ввода")

# =====================
# ▶️ ЗАПУСК
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(button))

print("🔥 BOT RUNNING")
app.run_polling()
