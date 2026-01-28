import asyncio
import logging
import uuid
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

BOT_TOKEN = "8536282991:AAFDzgiXbhJG-GSuKci04oLy3Ny4bpdD9Yw"
CRYPTOBOT_TOKEN = "522930:AAl0Ojn6IiEeAZH2NP2nZ4ZjUgBR6getqjL"

CRYPTO_API_URL = "https://pay.crypt.bot/api"

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# user_id -> total usdt
users_spent = {}

# invoice_id -> user_id
pending_invoices = {}


def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Въебать 10 USDT", callback_data="buy_10")],
        [InlineKeyboardButton(text="💸 Въебать 50 USDT", callback_data="buy_50")],
        [InlineKeyboardButton(text="🏆 Топ", callback_data="top")],
    ])


async def create_invoice(amount: float, user_id: int):
    invoice_id = str(uuid.uuid4())

    payload = {
        "asset": "USDT",
        "amount": amount,
        "description": "BeRich Banana — понты",
        "payload": invoice_id,
        "allow_comments": False,
        "allow_anonymous": False
    }

    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CRYPTO_API_URL}/createInvoice",
            json=payload,
            headers=headers
        ) as resp:
            data = await resp.json()

    if not data.get("ok"):
        raise Exception(data)

    pending_invoices[invoice_id] = user_id
    return data["result"]["pay_url"], invoice_id


async def check_invoice(invoice_id: str):
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{CRYPTO_API_URL}/getInvoices?invoice_ids={invoice_id}",
            headers=headers
        ) as resp:
            data = await resp.json()

    if not data.get("ok"):
        return None

    invoices = data["result"]["items"]
    return invoices[0] if invoices else None


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🍌 BeRich BANANA (Crypto)\n\n"
        "Ты тратишь реальные деньги,\n"
        "чтобы все видели, сколько ты въебал.\n\n"
        "USDT. Понты. Ничего взамен.",
        reply_markup=main_kb()
    )


@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: CallbackQuery):
    amount = float(call.data.split("_")[1])

    pay_url, invoice_id = await create_invoice(amount, call.from_user.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
        [InlineKeyboardButton(
            text="🔄 Проверить оплату",
            callback_data=f"check_{invoice_id}"
        )]
    ])

    await call.message.answer(
        f"💸 Счёт на **{amount} USDT**\n\n"
        "Оплати и нажми «Проверить оплату».",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data.startswith("check_"))
async def check(call: CallbackQuery):
    invoice_id = call.data.replace("check_", "")
    invoice = await check_invoice(invoice_id)

    if not invoice:
        await call.answer("Счёт не найден", show_alert=True)
        return

    if invoice["status"] != "paid":
        await call.answer("Ещё не оплачено", show_alert=True)
        return

    uid = pending_invoices.get(invoice_id)
    amount = float(invoice["amount"])

    users_spent[uid] = users_spent.get(uid, 0) + amount
    pending_invoices.pop(invoice_id, None)

    await call.message.answer(
        f"💸 **ОПЛАЧЕНО**\n\n"
        f"Ты въебал: {amount} USDT\n"
        f"Всего: {users_spent[uid]} USDT",
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data == "top")
async def top(call: CallbackQuery):
    if not users_spent:
        await call.message.answer("Пока никто не богат")
    else:
        text = "🏆 ТОП\n"
        for i, (uid, amount) in enumerate(
            sorted(users_spent.items(), key=lambda x: x[1], reverse=True), 1
        ):
            text += f"{i}. {uid}: {amount} USDT\n"

        await call.message.answer(text)

    await call.answer()


async def main():
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
