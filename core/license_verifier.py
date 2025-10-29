import json
import base64
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# 🔑 المفتاح العام الذي يقابل المفتاح الخاص في مولد الأكواد
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvbPY6p4tvE5YF0Fd23Xk
b7qkEZ4yLUEK1FqE3r6bn3a3XSwcK1y/3N9wxA8z1K6EMXslx+KjXIfZ6bEaxPrR
bCwTkqCT0Sn2UjE0K4DdCCdLw2UN6bFeaF6D3J0BzgpzYBz19BfZzMJg5HvYHz1f
C2DBgHDlRpVvW8DlqHY+je3TDC1iNQIDAQAB
-----END PUBLIC KEY-----"""


def verify_license():
    license_path = Path(__file__).resolve().parent.parent / "license.json"
    if not license_path.exists():
        return "❌ No license file found"

    with open(license_path, "r") as f:
        data = json.load(f)

    signature_b64 = data.pop("signature", None)
    if not signature_b64:
        return "❌ Missing signature"

    signature = base64.b64decode(signature_b64)
    message = json.dumps(data, sort_keys=True).encode()

    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)

    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return f"✅ Valid license for: {data.get('clinic_name')} until {data.get('valid_until')}"
    except Exception as e:
        return f"❌ Invalid license signature: {e}"
