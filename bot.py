import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8536282991:AAFDzgiXbhJG-GSuKci04oLy3Ny4bpdD9Yw"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# user_id -> total stars
users_spent = {}


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Мой рейтинг", callback_data="my_rating")],
        [InlineKeyboardButton(text="⭐ Въебать Stars", callback_data="send_stars")]
    ])


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🍌 Banana BeRich\n\n"
        "Ты тратишь ⭐ Telegram Stars,\n"
        "чтобы все видели, сколько ты въебал.",
        reply_markup=main_keyboard()
    )


@dp.callback_query(F.data == "my_rating")
async def my_rating(call: CallbackQuery):
    uid = call.from_user.id
    total = users_spent.get(uid, 0)

    sorted_users = sorted(users_spent.items(), key=lambda x: x[1], reverse=True)
    place = next((i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid), None)

    text = "🏆 ТОП\n"
    for i, (u, stars) in enumerate(sorted_users[:10], 1):
        mark = " ← ты" if u == uid else ""
        text += f"{i}. {u}: ⭐ {stars}{mark}\n"

    text += "\n"
    text += f"Твой статус: ⭐ {total}\n"
    if place:
        text += f"Место: {place}"

    await call.message.answer(text)
    await call.answer()


@dp.callback_query(F.data == "send_stars")
async def send_stars(call: CallbackQuery):
    prices = [
        LabeledPrice(label="Абсолютно ничего", amount=100)  # 100 ⭐
    ]

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="🍌 Banana Stars",
        description="Сатира. Ты платишь за понт.",
        payload="banana_stars_100",
        currency="XTR",
        prices=prices
    )
    await call.answer()


@dp.pre_checkout_query()
async def pre_checkout(pre: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre.id, ok=True)


@dp.message(F.successful_payment)
async def success(message: Message):
    stars = message.successful_payment.total_amount
    uid = message.from_user.id

    users_spent[uid] = users_spent.get(uid, 0) + stars

    await message.answer(
        f"💸 УСПЕХ\n"
        f"Ты въебал: ⭐ {stars}\n"
        f"Всего: ⭐ {users_spent[uid]}"
    )


async def main():
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
