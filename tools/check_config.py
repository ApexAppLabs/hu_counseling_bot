"""
Quick diagnostic script to check bot configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("BOT CONFIGURATION CHECK")
print("=" * 50)

# Check BOT_TOKEN
bot_token = os.getenv('BOT_TOKEN')
if bot_token:
    print(f"✅ BOT_TOKEN: Set (starts with: {bot_token[:10]}...)")
else:
    print("❌ BOT_TOKEN: NOT SET!")

# Check CHANNEL_ID
channel_id = os.getenv('CHANNEL_ID')
if channel_id:
    print(f"✅ CHANNEL_ID: {channel_id}")
else:
    print("❌ CHANNEL_ID: NOT SET!")

# Check ADMIN_IDS
admin_ids_str = os.getenv('ADMIN_IDS', '')
if admin_ids_str:
    admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    print(f"✅ ADMIN_IDS: {admin_ids}")
    print(f"   Number of admins: {len(admin_ids)}")
else:
    print("❌ ADMIN_IDS: NOT SET OR EMPTY!")
    print("   ⚠️  Admin functionality will NOT work!")

print("=" * 50)
print("\nYour .env file should look like:")
print("BOT_TOKEN=your_token_here")
print("CHANNEL_ID=@haruconfessions")
print("ADMIN_IDS=8352539365")
print("=" * 50)
