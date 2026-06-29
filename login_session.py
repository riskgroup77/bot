"""
Telethon sessiyasini bir marta yaratish uchun skript.
Faqat shu faylni ishga tushiring, kodni kiriting — keyin fergana.py kod so'ramaydi.
"""
import asyncio

from fergana import account1_config, ensure_telethon_session


async def main():
    print("Telegram akkauntiga kirish...")
    success = await ensure_telethon_session(account1_config)
    if success:
        print("\nTayyor! Endi `python fergana.py` ni ishga tushirishingiz mumkin.")
    else:
        print("\nKirish amalga oshmadi. Bir necha daqiqa kutib qayta urinib ko'ring.")


if __name__ == "__main__":
    asyncio.run(main())
