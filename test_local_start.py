"""
Test if bot can start locally
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 60)

required_vars = ['BOT_TOKEN', 'CHANNEL_ID', 'ADMIN_IDS', 'WEBHOOK_URL']

for var in required_vars:
    value = os.getenv(var)
    if value:
        if var == 'BOT_TOKEN':
            print(f"[OK] {var}: {value[:15]}... (exists)")
        else:
            print(f"[OK] {var}: {value}")
    else:
        print(f"[MISSING] {var}: NOT SET")

print("\n" + "=" * 60)
print("TESTING BOT IMPORTS")
print("=" * 60)

try:
    print("Importing bot_webhook...")
    import bot_webhook
    print("[OK] bot_webhook imported successfully")
    
    print("\nChecking bot configuration...")
    print(f"  BOT_TOKEN: {'Set' if bot_webhook.BOT_TOKEN else 'Missing'}")
    print(f"  CHANNEL_ID: {'Set' if bot_webhook.CHANNEL_ID else 'Missing'}")
    print(f"  ADMIN_IDS: {bot_webhook.ADMIN_IDS}")
    
except Exception as e:
    print(f"[ERROR] importing bot_webhook: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())

print("\n" + "=" * 60)
