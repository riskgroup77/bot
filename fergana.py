import asyncio
import logging
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ==============================================================================
# 1. KUTUBXONALARNI IMPORT QILISH
# ==============================================================================

# Telethon kutubxonasi (Spammer uchun)
from telethon import TelegramClient, events
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)

# Python-telegram-bot kutubxonasi (Bot uchun)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

# ==============================================================================
# 2. SPAMMER UCHUN SOZLAMALAR
# ==============================================================================
# 1-AKKAUNT
account1_config = {
    'session_name': 'session_accountFergana',
    'api_id': 33086552,
    'api_hash': '0e7280c95def86a8e881193227e12d5c',
    'phone_number': '+998911205090',
    'target_groups': ['https://t.me/katta_shafyorlar']
}



# KALIT SO'ZLAR
def generate_keywords():
    keywords = [
        'odam bor',
        'одом бор',
        'рошта бор',
        'рочта бор',
        'pochta bot',
        'mashina kerak',
        'mashin kerak',
        'мошина керак',
        'мошин керак',
        'машина керак',
        'машин керак',
    ]
    return list(set(k.lower() for k in keywords))

KEYWORDS = generate_keywords()

# TAQIQLANGAN SO'ZLAR RO'YXATI
# Ushbu so'zlar xabarda bo'lsa, xabar yuborilmaydi
FORBIDDEN_PHRASES = [
    'ayol kishi bor',    # Lotin
    'аёл киши бор',      # Kirill
    'ayol kishi bilan',  # Qo'shimcha variant
    'аёл киши билан',    # Qo'shimcha variant
    'женщина есть',      # Ruscha variant
    'с женщиной',        # Ruscha variant
    'женщины есть'       # Ruscha variant (ko'plikda)
]
# Barcha taqiqlangan so'zlarni kichik harfga o'tkazamiz
FORBIDDEN_PHRASES = [phrase.lower() for phrase in FORBIDDEN_PHRASES]


# ==============================================================================
# 3. BOT UCHUN SOZLAMALAR
# ==============================================================================
BOT_TOKEN = "8169464930:AAFFwZ25lB7FfYN4ZXSKRpL2PtO4uTBYzM81"
ADMIN_USER_ID = 213806260  # O'zingizning Telegram user ID'ingizni yozing

# Guruh linklari (global o'zgaruvchi sifatida)
PASSENGERS_GROUP_LINKS = [
    "https://t.me/Uchkoprik_Toshkent_taksi_77",
    "https://t.me/Buvayda_Toshkent_taksi_77",
    "https://t.me/Bogdod_Toshkent_taksi_77",
    "https://t.me/Rishton_Toshkent_taksi_77"
]

# Holatlar uchun steyte'lar
(CHOOSING, PASSENGER_INFO) = range(2)

# Tugmalar
main_keyboard = ReplyKeyboardMarkup([["🚖 Taksi kerak"]], resize_keyboard=True)
cancel_keyboard = ReplyKeyboardMarkup([["Bekor qilish"]], resize_keyboard=True)

WELCOME_GROUPS_TEXT = (
    "🚕 Toshkent yo'nalishidagi eng faol taksi guruhlari!\n"
    "Quyidagi guruhlarga qo'shiling va kerakli yo'nalishda tez va oson taksi toping yoki haydovchi bo'ling:\n\n"
    "🔗 <a href='https://t.me/Uchkoprik_Toshkent_taksi_77'>Uchko'prik - Toshkent</a>\n\n"
    "🔗 <a href='https://t.me/Buvayda_Toshkent_taksi_77'>Buvayda - Toshkent</a>\n\n"
    "🔗 <a href='https://t.me/Bogdod_Toshkent_taksi_77'>Bog'dod - Toshkent</a>\n\n"
    "🔗 <a href='https://t.me/Rishton_Toshkent_taksi_77'>Rishton - Toshkent</a>\n\n"
    "Guruhga qo'shiling va yo'lda qolmang! 🚖\n\n"
    "ℹ️ Savollar bo'lsa, +998770805090 bilan bog'laning."
)


# ==============================================================================
# 4. SPAMMER FUNKSIYALARI (Telethon)
# ==============================================================================

async def add_spammer_event_handler(client, config):
    phone = config['phone_number']
    print(f"🎧 [SPAMMER - {phone}] Barcha guruh/kanallardan xabarlarni kuzatishni boshladi.")

    @client.on(events.NewMessage)
    async def handler(event):
        # 1. Asosiy tekshiruvlar: xabar shaxsiy emasligi, bo'sh emasligi, guruhdanligi
        if event.is_private or not event.raw_text or not event.is_group:
            return

        try:
            sender = await event.get_sender()
        except ChannelPrivateError:
            return

        if not sender:
            return

        if getattr(sender, 'bot', False):
            return
        # .lower() metodi 'bot', 'Bot', '_bot', 'MyBot' kabi barcha variantlarni qamrab oladi
        if sender.username and 'bot' in sender.username.lower():
            print(f"🚫 [FILTER - USERNAME] @{sender.username} nomida 'bot' so'zi borligi uchun xabar o'tkazib yuborildi.")
            return

        message_text = event.raw_text.lower()

        # 3. Xabar matnida taqiqlangan so'zlar borligini tekshirish
        if any(phrase in message_text for phrase in FORBIDDEN_PHRASES):
            print(f"🚫 [FILTER - PHRASE] Taqiqlangan so'z topilgani uchun xabar o'tkazib yuborildi: {event.raw_text[:40]}...")
            return
        
        # <<< YANGILANGAN QISM TUGADI

        # 4. Asosiy kalit so'zlar mavjudligini tekshirish
        if any(keyword in message_text for keyword in KEYWORDS):
            # Yuboruvchi ma'lumotlari yuqorida olingan, qayta chaqirish shart emas
            user_link = f"@{sender.username}" if sender.username else f"[{sender.first_name}](tg://user?id={sender.id})"

            chat = await event.get_chat()
            group_link = f"https://t.me/{chat.username}/{event.message.id}" if hasattr(chat, 'username') and chat.username else f"https://t.me/c/{chat.id}/{event.message.id}"

            # >>> O'ZGARTIRILGAN QISM: XABAR FORMATI
            # Original xabar endi oddiy matn ko'rinishida, `...` belgilarsiz yuboriladi.
            message_to_forward = (
                f"**❗️ Yangi e'lon topildi!**\n\n"
                f"**👤 Foydalanuvchi:** {user_link}\n"
                f"**📍 Guruhdan:** [Xabarga o'tish]({group_link})\n\n"
                f"**Original xabar:**\n{event.raw_text}"  # Matn oddiy shaklda, formatlashsiz
            )
            # <<< O'ZGARTIRILGAN QISM TUGADI

            for target_group in config['target_groups']:
                try:
                    # link_preview=False qo'shildi, bu xabardagi linklar uchun oldindan ko'rishni o'chiradi
                    await client.send_message(target_group, message_to_forward, parse_mode='md', link_preview=False)
                except Exception as e:
                    print(f"XATOLIK [SPAMMER - {phone} -> {target_group}]: {e}")

            print(f"✅ [SPAMMER - {phone}] xabar yubordi: {event.raw_text[:30]}...")


def clean_session_files(session_name):
    """Telethon sessiya fayllarini to'liq o'chiradi."""
    removed = []
    for name in os.listdir('.'):
        if name == f"{session_name}.session" or name.startswith(f"{session_name}.session-"):
            try:
                os.remove(name)
                removed.append(name)
            except OSError as e:
                print(f"⚠️  {name} o'chirilmadi: {e}")
    return removed


def _describe_code_delivery(sent, phone):
    """Kod qayerga yuborilganini tushuntiradi."""
    code_type = type(sent.type).__name__
    if code_type == 'SentCodeTypeApp':
        return (
            "Kod TELEGRAM ILOVASIGA yuborildi.\n"
            f"  -> Telegram ni oching ({phone} bilan kirilgan)\n"
            "  -> Yuqoridagi 'Chat' ikonkasi -> 'Telegram' xizmat xabari\n"
            "  -> Eng oxirgi xabardagi 5 xonali kodni oling"
        )
    if code_type == 'SentCodeTypeSms':
        return f"Kod SMS orqali yuborildi: {phone}"
    if code_type == 'SentCodeTypeCall':
        return f"Kod TELEFON QO'NG'IROG'I orqali aytiladi: {phone}"
    return f"Kod yuborildi (tur: {code_type})"


def _read_login_code():
    """Terminaldan kod o'qish."""
    while True:
        code = input("Kodni kiriting (faqat raqamlar): ").strip().replace(" ", "")
        if code.isdigit() and len(code) >= 5:
            return code
        print("Noto'g'ri format. Masalan: 12345")


async def ensure_telethon_session(config, clean=False, force_sms=False):
    """Telegram akkauntiga kirish. clean=True bo'lsa eski sessiyani o'chiradi."""
    session_name = config['session_name']
    session_path = f"{session_name}.session"
    phone = config['phone_number']

    if clean:
        removed = clean_session_files(session_name)
        if removed:
            print(f"🗑️  O'chirildi: {', '.join(removed)}")
        else:
            print("🗑️  O'chiriladigan sessiya topilmadi.")

    client = TelegramClient(session_name, config['api_id'], config['api_hash'])
    await client.connect()

    if await client.is_user_authorized():
        print(f"✅ [SPAMMER] Mavjud sessiya topildi ({session_path}). Kod kerak emas.")
        await client.disconnect()
        return True

    # Yarim sessiya loginni buzishi mumkin — tozalaymiz
    await client.disconnect()
    clean_session_files(session_name)
    client = TelegramClient(session_name, config['api_id'], config['api_hash'])
    await client.connect()

    print("\n" + "=" * 50)
    print(f"📱 TELEGRAM KIRISH: {phone}")
    print("=" * 50)

    try:
        sent = await client.send_code_request(phone, force_sms=force_sms)
        print(_describe_code_delivery(sent, phone))
        print("=" * 50)
        print("DIQQAT: Kod 2-3 daqiqada eskiradi. Tez kiriting!")
        print("Agar kod kelmasa: python login_session.py --sms")
        print("=" * 50 + "\n")

        for attempt in range(3):
            try:
                code = _read_login_code()
                await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
                break
            except PhoneCodeInvalidError:
                print("❌ Noto'g'ri kod. Qayta urinib ko'ring (yangi kod kerak bo'lishi mumkin).")
                if attempt == 2:
                    raise
            except PhoneCodeExpiredError:
                print("⏰ Kod eskirgan. Yangi kod so'ralmoqda...")
                sent = await client.send_code_request(phone, force_sms=force_sms)
                print(_describe_code_delivery(sent, phone))

        print(f"✅ [SPAMMER] {phone} muvaffaqiyatli ro'yxatdan o'tdi!")
        print(f"✅ Sessiya saqlandi: {session_path}")
        await client.disconnect()
        return True

    except SessionPasswordNeededError:
        print("\n🔐 Akkountda 2 bosqichli parol yoqilgan.")
        password = input("2FA parolni kiriting: ").strip()
        await client.sign_in(password=password)
        print(f"✅ [SPAMMER] {phone} parol bilan muvaffaqiyatli kirdi!")
        await client.disconnect()
        return True
    except FloodWaitError as e:
        minutes = max(1, e.seconds // 60)
        print(f"❌ [SPAMMER] Telegram cheklovi: {e.seconds} soniya ({minutes} daqiqa) kuting.")
        print("   Sabab: juda ko'p marta kod so'ralgan. Kutib, keyin qayta urinib ko'ring.")
    except PhoneCodeInvalidError:
        print("❌ [SPAMMER] Kod 3 marta noto'g'ri kiritildi. Sessiyani tozalab qayta urinib ko'ring:")
        print("   python login_session.py --clean")
    except Exception as e:
        print(f"❌ [SPAMMER] Kirish xatoligi ({type(e).__name__}): {e}")
    finally:
        if client.is_connected():
            await client.disconnect()
    return False


async def run_telethon_client(config):
    client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
    phone = config['phone_number']

    print(f"\n>>> [SPAMMER] {phone} akkauntiga ulanmoqda...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"❌ [SPAMMER] Sessiya yaroqsiz yoki muddati tugagan.")
            print("⚠️  Lokal kompyuterdan login qiling: python login_session.py --clean")
            return
        print(f"✅ [SPAMMER] {phone} muvaffaqiyatli ulandi!")
    except Exception as e:
        print(f"❌ [SPAMMER] {phone} ulanishda xatolik ({type(e).__name__}): {e}")
        return

    await add_spammer_event_handler(client, config)
    await client.run_until_disconnected()

async def run_spammer():
    """Telethon qismini ishga tushuruvchi asosiy funksiya."""
    print("\n🚀 SPAMMER QISMI ISHGA TUSHMOQDA...")
    tasks = [
        run_telethon_client(account1_config)
    ]
    await asyncio.gather(*tasks)

# ==============================================================================
# 5. BOT FUNKSIYALARI (python-telegram-bot)
# ==============================================================================

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchiga matn, guruh linklari va tugmalarni ko'rsatadi."""
    user = update.effective_user
    caption = (
        f"Assalomu alaykum, {user.first_name}!\nXush kelibsiz!\n\n"
        f"📍 Toshkent - Bog'dod yo'nalishi uchun taksi xizmatini tez va oson toping!\n\n"
        f"🚖 Taksi kerak: Agar sizga taksi kerak bo'lsa, o'z ma'lumotlaringizni qoldiring va haydovchilar siz bilan bog'lanishadi.\n\n"
        f"{WELCOME_GROUPS_TEXT}"
    )
    await update.message.reply_text(caption, parse_mode='HTML', reply_markup=main_keyboard, disable_web_page_preview=True)
    return CHOOSING

async def choose_bot_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchi tugma tanlaganda mos jarayonni boshlaydi."""
    if update.message.text == "🚖 Taksi kerak":
        await update.message.reply_text(
            "Ismingiz va telefon raqamingizni kiriting:\n(Masalan: Ali 998901234567)",
            reply_markup=cancel_keyboard
        )
        return PASSENGER_INFO
    else:
        await update.message.reply_text("Iltimos, quyidagi tugmalardan birini tanlang.", reply_markup=main_keyboard)
        return CHOOSING

async def get_passenger_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Yo'lovchi ism va telefonini oladi va guruhlarga yuboradi."""
    data = update.message.text.strip()
    parts = data.split()
    name = ' '.join(parts[:-1]) if len(parts) > 1 else data
    phone = parts[-1] if len(parts) > 1 else "-"

    for group_link in PASSENGERS_GROUP_LINKS:
        try:
            chat_identifier = group_link.split('/')[-1]
            if not chat_identifier.startswith('t.me/+'):
                chat_identifier = '@' + chat_identifier

            await context.bot.send_message(
                chat_id=chat_identifier,
                text=f"🧾 Yangi yo'lovchi:\n👤 Ismi: {name}\n📞 Tel: {phone}",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"XATOLIK [BOT -> {group_link}]: {e}")
            await update.message.reply_text(f"'{group_link}' guruhiga yuborishda xatolik yuz berdi. Iltimos, admin bilan bog'laning.")
            continue

    await update.message.reply_text("Ma'lumotlaringiz tegishli guruhlarga yuborildi!", reply_markup=main_keyboard)
    return CHOOSING

async def cancel_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Foydalanuvchi dialogni bekor qilsa, boshlang'ich menyuga qaytaradi."""
    await update.message.reply_text("Asosiy menyuga qaytdingiz.", reply_markup=main_keyboard)
    return ConversationHandler.END

async def run_bot():
    """PTB bot qismini ishga tushuruvchi asosiy funksiya."""
    print("\n🚀 BOT QISMI ISHGA TUSHMOQDA...")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_bot)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_bot_action)],
            PASSENGER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passenger_info)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Bekor qilish$"), cancel_bot), CommandHandler('cancel', cancel_bot)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)

    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("✅ BOT muvaffaqiyatli ishga tushdi.")
    except Exception as e:
        print(f"XATOLIK [BOT]: Botni ishga tushirishda muammo: {e}")
        if "401" in str(e) or "Unauthorized" in str(e) or "rejected" in str(e).lower():
            print("⚠️  BOT_TOKEN noto'g'ri yoki bekor qilingan.")
            print("⚠️  @BotFather dan yangi token oling va fergana.py dagi BOT_TOKEN ni almashtiring.")


# ==============================================================================
# 6. ASOSIY ISHGA TUSHIRISH FUNKSIYASI
# ==============================================================================

async def main():
    """Ikkala dasturni (Spammer va Bot) bir vaqtda ishga tushiradi."""

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    print("="*50)
    print("Dastur ishga tushdi...")
    print(f"Qidirilayotgan kalit so'zlar: {KEYWORDS}")
    print(f"Taqiqlangan so'zlar/jumlalar: {FORBIDDEN_PHRASES}")
    print("="*50)

    # Sessiya tekshiruvi (faqat fayl mavjudligi emas, haqiqiy avtorizatsiya)
    session_file = f"{account1_config['session_name']}.session"
    if os.path.exists(session_file):
        check_client = TelegramClient(
            account1_config['session_name'],
            account1_config['api_id'],
            account1_config['api_hash'],
        )
        await check_client.connect()
        authorized = await check_client.is_user_authorized()
        await check_client.disconnect()
        if authorized:
            print(f"✅ [SPAMMER] Sessiya faol ({session_file}).")
        else:
            print(f"⚠️  [SPAMMER] Sessiya fayli bor, lekin avtorizatsiya yo'q.")
            if sys.stdin.isatty():
                await ensure_telethon_session(account1_config)
            else:
                print("⚠️  Server rejimi: python login_session.py --clean ni lokalda ishga tushiring.")
    else:
        if sys.stdin.isatty():
            if not await ensure_telethon_session(account1_config):
                print("\n⚠️  Spammer qismi ishlamaydi. Avval login qiling.\n")
        else:
            print("\n⚠️  Sessiya topilmadi. login_session.py orqali kirish kerak.\n")

    spammer_task = asyncio.create_task(run_spammer())
    bot_task = asyncio.create_task(run_bot())

    # Spammer asosiy jarayon — u ishlayotguncha dastur yashaydi
    await spammer_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Dastur to'xtatildi.")
    except Exception as e:
        print(f"\nKUTILMAGAN UMUMIY XATOLIK: {e}")