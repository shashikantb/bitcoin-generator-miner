import os
import hashlib
import ecdsa
import base58

def generate_private_key():
    """Generates a random 32-byte private key."""
    return os.urandom(32)

def private_key_to_wif(private_key):
    """Converts a private key to Wallet Import Format (WIF)."""
    # 1. Add version byte (0x80 for Mainnet)
    version_byte = b'\x80'
    extended_key = version_byte + private_key
    
    # 2. Perform double SHA-256 hash
    sha256_1 = hashlib.sha256(extended_key).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    
    # 3. Take first 4 bytes as checksum
    checksum = sha256_2[:4]
    
    # 4. Add checksum to extended key
    final_key = extended_key + checksum
    
    # 5. Encode in Base58
    wif = base58.b58encode(final_key)
    return wif.decode('utf-8')

def private_key_to_public_key(private_key):
    """Derives the public key from the private key using SECP256k1."""
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    # Add prefix 0x04 for uncompressed public key
    return b'\x04' + vk.to_string()

def public_key_to_address(public_key):
    """Converts a public key to a Bitcoin address."""
    # 1. SHA-256 hash of public key
    sha256_pub = hashlib.sha256(public_key).digest()
    
    # 2. RIPEMD-160 hash of SHA-256 result
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_pub)
    ripemd_pub = ripemd160.digest()
    
    # 3. Add version byte (0x00 for Mainnet)
    version_byte = b'\x00'
    extended_ripemd = version_byte + ripemd_pub
    
    # 4. Double SHA-256 hash for checksum
    sha256_1 = hashlib.sha256(extended_ripemd).digest()
    sha256_2 = hashlib.sha256(sha256_1).digest()
    
    # 5. Take first 4 bytes as checksum
    checksum = sha256_2[:4]
    
    # 6. Add checksum to extended ripemd
    binary_address = extended_ripemd + checksum
    
    # 7. Encode in Base58
    address = base58.b58encode(binary_address)
    return address.decode('utf-8')

def generate_wallet():
    """Generates a new Bitcoin wallet (Private Key & Address)."""
    print("Generating a new Bitcoin wallet...")
    print("-----------------------------------")
    
    private_key = generate_private_key()
    wif_key = private_key_to_wif(private_key)
    public_key = private_key_to_public_key(private_key)
    address = public_key_to_address(public_key)
    
    print(f"Private Key (WIF): {wif_key}")
    print(f"Bitcoin Address:   {address}")
    print("-----------------------------------")
    print("IMPORTANT: This is a newly generated wallet. It has 0 balance.")
    print("To use it, you must transfer Bitcoin to the address above.")
    print("DO NOT SHARE YOUR PRIVATE KEY WITH ANYONE.")

if __name__ == "__main__":
    generate_wallet()
