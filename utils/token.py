import base64
import json

def encode_token(data: dict) -> str:
    return base64.urlsafe_b64encode(
        json.dumps(data).encode()
    ).decode()

def decode_token(token: str) -> dict:
    return json.loads(
        base64.urlsafe_b64decode(token.encode()).decode()
    )
