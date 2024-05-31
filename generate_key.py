import secrets

def generate_api_key(length=16):
    """Generate a secure random API key."""
    return secrets.token_hex(length)

# API 키 생성
api_key = generate_api_key()
print("Generated API Key:", api_key)
