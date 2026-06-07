# fix_key.py
import json
import base64

with open('credentials.json', 'r') as f:
    creds = json.load(f)

print("=== COPY EVERYTHING BELOW ===")
print()
print(f'type = "{creds["type"]}"')
print(f'project_id = "{creds["project_id"]}"')
print(f'private_key_id = "{creds["private_key_id"]}"')

# Fix private key format
key = creds['private_key']
print(f'private_key = """{key}"""')

print(f'client_email = "{creds["client_email"]}"')
print(f'client_id = "{creds["client_id"]}"')
print(f'auth_uri = "{creds["auth_uri"]}"')
print(f'token_uri = "{creds["token_uri"]}"')
print(f'auth_provider_x509_cert_url = "{creds["auth_provider_x509_cert_url"]}"')
print(f'client_x509_cert_url = "{creds["client_x509_cert_url"]}"')