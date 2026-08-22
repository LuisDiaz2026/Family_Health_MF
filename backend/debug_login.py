import os
import sys
import django
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from django.test import Client

client = Client()

print("Testing login cliente1_fh...")
resp = client.post(
    "/api/v1/auth/login/",
    data=json.dumps({"username": "cliente1_fh", "password": "Cliente1FH*!"}),
    content_type="application/json",
)
print(f"STATUS: {resp.status_code}")
print(f"CONTENT-TYPE: {resp.get('Content-Type')}")
print("BODY:")
try:
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception:
    print(resp.content.decode("utf-8", errors="replace"))
