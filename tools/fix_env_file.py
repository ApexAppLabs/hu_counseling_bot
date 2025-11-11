"""
Fix .env file encoding and format
"""
import os

print("=" * 60)
print("FIXING .ENV FILE")
print("=" * 60)

# Backup the old file first
old_env = '.env'
backup_env = '.env.backup'

if os.path.exists(old_env):
    print(f"\n1. Creating backup: {backup_env}")
    with open(old_env, 'rb') as f:
        content = f.read()
    with open(backup_env, 'wb') as f:
        f.write(content)
    print("   Backup created!")

# Copy the correct .env file
correct_env = '.env.correct'
if os.path.exists(correct_env):
    print(f"\n2. Copying corrected .env file...")
    with open(correct_env, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Write without BOM
    with open(old_env, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   .env file updated!")
    
    print("\n3. Verifying new .env file...")
    with open(old_env, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key = line.split('=')[0] if '=' in line else ''
                print(f"   Found: {key}")
    
    print("\n" + "=" * 60)
    print("SUCCESS! .env file fixed")
    print("=" * 60)
    print("\nYou can now run: python bot_professional.py")
    print("Or test with: python check_env.py")
else:
    print(f"\nERROR: {correct_env} not found!")
    print("\nPlease manually create .env file with this content:")
    print("-" * 60)
    print("BOT_TOKEN=8584851548:AAGq2wCnaK9_7YTY9hTw1T-J81i9MmbHS50")
    print("CHANNEL_ID=@haruconfessions")
    print("ADMIN_IDS=8352539365")
    print("WEBHOOK_URL=https://young-cele-anonymousaccounts-1b8d8d1a.koyeb.app")
    print("-" * 60)
    print("\nMake sure to save as UTF-8 (NO BOM)!")
