# by @itschalondra

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_GROUP_ID
from utils.logger import setup_logger
from utils.theme import WELCOME_MESSAGES
from utils.format_text import generate_order_format
from utils.database import update_mapping

setup_logger()

app = Client(
    "blakeshley_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Simpan mapping ID pesan -> user ID
forwarded_messages = {}

# === START COMMAND ===
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    chat_id = message.chat.id

    try:
        first = await client.send_message(chat_id, WELCOME_MESSAGES[0])
        await asyncio.sleep(3)
        await first.delete()

        second = await client.send_message(chat_id, WELCOME_MESSAGES[1])
        await asyncio.sleep(3)
        await second.delete()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᯓ ✎ format your wishes ✎", callback_data="format")]
        ])
        await client.send_message(
            chat_id,
            WELCOME_MESSAGES[2],
            reply_markup=keyboard
        )

    except Exception as e:
        app.logger.error(f"Terjadi kesalahan saat mengirim pesan start: {e}")

# === CALLBACK TOMBOL "format" ===
@app.on_callback_query(filters.regex("format"))
async def format_button(client, callback_query):
    try:
        await callback_query.answer()
        username = callback_query.from_user.username or "username"

        text = generate_order_format(username)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᯓ ✎ Copy Here", switch_inline_query_current_chat=text)]
        ])

        formatted_text = f"*Copy and Paste This:*\n\n```{text}```"
        sent = await callback_query.message.reply_text(
            formatted_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        await asyncio.sleep(420)
        await sent.delete()

        try:
            await callback_query.message.delete()
        except Exception as e:
            app.logger.warning(f"Gagal menghapus pesan tombol format: {e}")

        await client.send_message(
            callback_query.message.chat.id,
            "༄ the magic fades into the mist... ༄"
        )

    except Exception as e:
        app.logger.error(f"Terjadi kesalahan dalam alur tombol format: {e}")

# === FITUR REPLY-BOT ===
@app.on_message(filters.private & ~filters.command(["start"]))
async def forward_user_message(client, message):
    try:
        sent = await message.forward(ADMIN_GROUP_ID)
        forwarded_messages[sent.id] = message.chat.id
    except Exception as e:
        app.logger.error(f"Error forwarding message: {e}")

@app.on_message(filters.group & filters.reply)
async def admin_reply_message(client, message):
    try:
        reply_to_id = message.reply_to_message.id
        user_id = forwarded_messages.get(reply_to_id)

        if user_id:
            await client.send_message(chat_id=user_id, text=message.text)
    except Exception as e:
        app.logger.error(f"Error sending reply to user: {e}")

# === RUN APP ===
if __name__ == "__main__":
    app.run()