"""
Complete diagnostic for Koyeb deployment
"""
import requests
import time

KOYEB_URL = "https://young-cele-anonymousaccounts-1b8d8d1a.koyeb.app"
BOT_TOKEN = "8584851548:AAGq2wCnaK9_7YTY9hTw1T-J81i9MmbHS50"

print("=" * 70)
print("COMPLETE KOYEB DEPLOYMENT DIAGNOSTIC")
print("=" * 70)

# Test 1: Check webhook status
print("\n[1] Telegram Webhook Status")
print("-" * 70)
try:
    response = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo",
        timeout=10
    )
    data = response.json()
    if data.get('ok'):
        result = data['result']
        print(f"Webhook URL: {result.get('url', 'NOT SET')}")
        print(f"Pending Updates: {result.get('pending_update_count', 0)}")
        if result.get('last_error_message'):
            print(f"Last Error: {result.get('last_error_message')}")
            print(f"Error Date: {result.get('last_error_date')}")
        else:
            print("Status: No errors")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Try all endpoints with detailed info
print("\n[2] Testing Koyeb Endpoints")
print("-" * 70)
endpoints = {
    "/": "Root",
    "/health": "Health Check",
    "/config": "Configuration Status",
    "/webhook": "Telegram Webhook (should be POST only)"
}

for path, description in endpoints.items():
    url = f"{KOYEB_URL}{path}"
    print(f"\n{description}: {path}")
    try:
        response = requests.get(url, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  JSON Response: {data}")
            except:
                print(f"  Text Response: {response.text[:200]}")
        elif response.status_code == 404:
            # Check if it's Koyeb's 404 or app's 404
            if "No active service" in response.text:
                print("  -> This is KOYEB's 404 (service not routed)")
            else:
                print("  -> This is app's 404 (service running, endpoint missing)")
    except requests.exceptions.Timeout:
        print("  ERROR: Request timeout")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Cannot connect to server")
    except Exception as e:
        print(f"  ERROR: {e}")

# Test 3: DNS and connectivity
print("\n[3] DNS and Network")
print("-" * 70)
import socket
hostname = "young-cele-anonymousaccounts-1b8d8d1a.koyeb.app"
try:
    ip = socket.gethostbyname(hostname)
    print(f"DNS Resolution: {hostname} -> {ip}")
except Exception as e:
    print(f"DNS Error: {e}")

# Test 4: Bot info
print("\n[4] Bot Information")
print("-" * 70)
try:
    response = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",
        timeout=10
    )
    data = response.json()
    if data.get('ok'):
        bot = data['result']
        print(f"Bot: @{bot.get('username')}")
        print(f"Name: {bot.get('first_name')}")
        print(f"ID: {bot.get('id')}")
except Exception as e:
    print(f"ERROR: {e}")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)

# Re-check main endpoint
try:
    response = requests.get(f"{KOYEB_URL}/health", timeout=10)
    if response.status_code == 200:
        print("\n✅ SUCCESS: Service is accessible and working!")
        print("   Next step: Test bot with /start command on Telegram")
    elif "No active service" in response.text:
        print("\n❌ PROBLEM: Koyeb routing issue")
        print("\n   Possible causes:")
        print("   1. Service deployed but not exposed publicly")
        print("   2. Wrong service name in Koyeb dashboard")
        print("   3. GitHub deployment not using correct branch")
        print("\n   Solutions:")
        print("   1. Check Koyeb Dashboard -> Your Service -> Settings")
        print("   2. Verify 'Public Routing' is enabled")
        print("   3. Check service URL matches: young-cele-anonymousaccounts-1b8d8d1a.koyeb.app")
        print("   4. Try manual redeploy")
    else:
        print(f"\n⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR: Cannot reach service - {e}")

print("\n" + "=" * 70)
