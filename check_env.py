"""
Check .env file content and format
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("CHECKING .ENV FILE")
print("=" * 60)

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f"\nLooking for: {env_path}")
print(f"Exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    print(f"\nFile size: {os.path.getsize(env_path)} bytes")
    
    print("\n--- RAW CONTENT ---")
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    print("--- END RAW CONTENT ---")

print("\n" + "=" * 60)
print("LOADING .ENV FILE")
print("=" * 60)

# Load the .env file
result = load_dotenv()
print(f"\nload_dotenv() returned: {result}")

print("\n" + "=" * 60)
print("CHECKING ENVIRONMENT VARIABLES")
print("=" * 60)

required_vars = ['BOT_TOKEN', 'CHANNEL_ID', 'ADMIN_IDS', 'WEBHOOK_URL']

for var in required_vars:
    value = os.getenv(var)
    if value:
        if var == 'BOT_TOKEN':
            print(f"\n[OK] {var}")
            print(f"     Value: {value[:20]}...")
        else:
            print(f"\n[OK] {var}")
            print(f"     Value: {value}")
    else:
        print(f"\n[MISSING] {var}")
        print(f"     Value: None")

print("\n" + "=" * 60)
