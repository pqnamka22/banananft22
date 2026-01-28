import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

from storage import users_spent, pending_invoices
from crypto import create_invoice, check_invoice

BOT_TOKEN = "8536282991:AAFDzgiXbhJG-GSuKci04oLy3Ny4bpdD9Yw"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Открыть BeRich",
                web_app=WebAppInfo(url="https://YOUR_DOMAIN/web/index.html")
            )
        ]
    ])


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🍌 **BeRich Banana**\n\n"
        "Ты тратишь деньги.\n"
        "Все видят, сколько.\n"
        "Ничего не получаешь.\n\n"
        "Заходи:",
        reply_markup=start_kb(),
        parse_mode="Markdown"
    )


@dp.message(F.web_app_data)
async def from_webapp(message: Message):
    # формат: pay:AMOUNT
    data = message.web_app_data.data

    if not data.startswith("pay:"):
        return

    amount = float(data.split(":")[1])
    user_id = message.from_user.id

    pay_url, invoice_id = await create_invoice(amount, user_id)
    pending_invoices[invoice_id] = user_id

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
        [InlineKeyboardButton(
            text="🔄 Проверить",
            callback_data=f"check:{invoice_id}"
        )]
    ])

    await message.answer(
        f"💸 Счёт на **{amount} USDT**",
        reply_markup=kb,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("check:"))
async def check(call):
    invoice_id = call.data.split(":")[1]
    invoice = await check_invoice(invoice_id)

    if not invoice or invoice["status"] != "paid":
        await call.answer("Не оплачено", show_alert=True)
        return

    uid = pending_invoices.pop(invoice_id)
    amount = float(invoice["amount"])

    users_spent[uid] = users_spent.get(uid, 0) + amount

    await call.message.answer(
        f"💸 **ОПЛАЧЕНО**\n\n"
        f"Ты въебал: {amount} USDT\n"
        f"Всего: {users_spent[uid]} USDT",
        parse_mode="Markdown"
    )
    await call.answer()


async def main():
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
