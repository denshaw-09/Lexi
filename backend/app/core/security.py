from web3 import Web3
import secrets
import time

def generate_nonce() -> str:
    return secrets.token_hex(16)

def verify_signature(address: str, signature: str, message: str) -> bool:
    try:
        w3 = Web3()
        message_hash = w3.keccak(text=message)
        recovered_address = w3.eth.account.recoverHash(message_hash, signature=signature)
        return recovered_address.lower() == address.lower()
    except:
        return False

def get_login_message(nonce: str) -> str:
    return f"Login to Nexus Agent. Nonce: {nonce}"