import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

BOT_TOKEN = "PASTE_BOT_TOKEN"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ====== ПРИМИТИВНОЕ ХРАНИЛИЩЕ (MVP) ======
users = {}  # user_id: total_stars

def add_stars(user_id: int, amount: int):
    users[user_id] = users.get(user_id, 0) + amount

def top_users(limit=10):
    return sorted(users.items(), key=lambda x: x[1], reverse=True)[:limit]

# ====== КНОПКИ ======
def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 100", callback_data="buy_100"),
            InlineKeyboardButton(text="⭐ 1 000", callback_data="buy_1000"),
        ],
        [
            InlineKeyboardButton(text="⭐ 10 000", callback_data="buy_10000"),
        ],
        [
            InlineKeyboardButton(text="🏆 Топ богачей", callback_data="top"),
            InlineKeyboardButton(text="👤 Мой статус", callback_data="me"),
        ]
    ])

# ====== /start ======
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🍌 **BeRich BANANA**\n\n"
        "Это сатирическая приложуха.\n"
        "Ты тратишь ⭐ Telegram Stars,\n"
        "чтобы все видели, сколько ты въебал.\n\n"
        "Никаких NFT. Никакой утилити.\n"
        "Только понты.\n\n"
        "Жми кнопки 👇",
        reply_markup=buy_keyboard(),
        parse_mode="Markdown"
    )

# ====== CALLBACKS ======
@dp.callback_query(F.data.startswith("buy_"))
async def buy(call):
    amount = int(call.data.split("_")[1])

    prices = [LabeledPrice(label="BeRich BANANA", amount=amount)]

    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title="🍌 BeRich BANANA",
        description=f"Показать всем, что ты потратил {amount} ⭐",
        payload=f"berich_{amount}",
        currency="XTR",
        prices=prices
    )
    await call.answer()

@dp.callback_query(F.data == "top")
async def show_top(call):
    top = top_users()
    if not top:
        text = "Пока никто не въебал ⭐"
    else:
        lines = ["🏆 **ТОП БОГАЧЕЙ**\n"]
        for i, (uid, stars) in enumerate(top, 1):
            lines.append(f"{i}. 👤 {uid} — ⭐ {stars}")
        text = "\n".join(lines)

    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "me")
async def me(call):
    total = users.get(call.from_user.id, 0)
    await call.message.answer(
        f"👤 **ТВОЙ СТАТУС**\n\n"
        f"Ты въебал:\n"
        f"⭐ **{total}**\n\n"
        f"Продолжай. Пусть завидуют.",
        parse_mode="Markdown"
    )
    await call.answer()

# ====== PRE-CHECKOUT ======
@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ====== УСПЕШНАЯ ОПЛАТА ======
@dp.message(F.successful_payment)
async def success(message: Message):
    stars = message.successful_payment.total_amount
    add_stars(message.from_user.id, stars)

    await message.answer(
        f"💸 **ПЛАТЁЖ ПРОШЁЛ**\n\n"
        f"Ты только что въебал:\n"
        f"⭐ **{stars}**\n\n"
        f"Теперь это видно.\n"
        f"Хочешь ещё?",
        reply_markup=buy_keyboard(),
        parse_mode="Markdown"
    )

# ====== /terms ======
@dp.message(F.text == "/terms")
async def terms(message: Message):
    await message.answer(
        "Это сатирический проект.\n"
        "Платежи — добровольная поддержка.\n"
        "Никаких NFT, инвестиций и возвратов."
    )

async def main():
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
