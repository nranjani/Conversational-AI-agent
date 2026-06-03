# get_secrets.py
import json

with open('credentials.json', 'r') as f:
    creds = json.load(f)
    print(json.dumps(creds, indent=2))