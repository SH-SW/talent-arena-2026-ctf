import base64, json, hmac, hashlib, time

SECRET = "dev-jwt-secret-do-not-use-in-production"

PAYLOAD = {
    "sub": "u-staff-5e6f7a8b",
    "email": "staff@companion.local",
    "role": "admin",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
payload = b64(json.dumps(PAYLOAD).encode())
sig = b64(hmac.new(SECRET.encode(), (header + "." + payload).encode(), hashlib.sha256).digest())

token = f"{header}.{payload}.{sig}"
print(token)
