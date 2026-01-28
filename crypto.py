import aiohttp
import uuid

CRYPTO_TOKEN = "522930:AAl0Ojn6IiEeAZH2NP2nZ4ZjUgBR6getqjL"
API_URL = "https://pay.crypt.bot/api"

HEADERS = {
    "Crypto-Pay-API-Token": CRYPTO_TOKEN
}


async def create_invoice(amount: float, user_id: int):
    invoice_id = str(uuid.uuid4())

    payload = {
        "asset": "USDT",
        "amount": amount,
        "description": "BeRich Banana — понты",
        "payload": invoice_id,
        "allow_anonymous": False
    }

    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{API_URL}/createInvoice",
            json=payload,
            headers=HEADERS
        ) as r:
            data = await r.json()

    if not data.get("ok"):
        raise Exception(data)

    return data["result"]["pay_url"], invoice_id


async def check_invoice(invoice_id: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(
            f"{API_URL}/getInvoices?invoice_ids={invoice_id}",
            headers=HEADERS
        ) as r:
            data = await r.json()

    if not data.get("ok"):
        return None

    items = data["result"]["items"]
    return items[0] if items else None
