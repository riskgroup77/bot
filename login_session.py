"""
Telethon sessiyasini yaratish uchun skript.

Ishlatish:
  python login_session.py           # oddiy kirish (kod Telegram ilovasiga)
  python login_session.py --clean   # eski sessiyani o'chirib, qayta kirish
  python login_session.py --sms     # kodni SMS orqali so'rash
  python login_session.py --clean --sms
"""
import argparse
import asyncio

from fergana import account1_config, ensure_telethon_session


async def main(clean, force_sms):
    print("Telegram akkauntiga kirish...")
    success = await ensure_telethon_session(
        account1_config,
        clean=clean,
        force_sms=force_sms,
    )
    if success:
        print("\nTayyor! Endi `python fergana.py` ni ishga tushirishingiz mumkin.")
    else:
        print("\nKirish amalga oshmadi.")
        if not force_sms:
            print("Kod kelmasa: python login_session.py --clean --sms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram sessiyasini yaratish")
    parser.add_argument("--clean", action="store_true", help="Eski sessiyani o'chirish")
    parser.add_argument("--sms", action="store_true", help="Kodni SMS orqali so'rash")
    args = parser.parse_args()
    asyncio.run(main(clean=args.clean, force_sms=args.sms))
