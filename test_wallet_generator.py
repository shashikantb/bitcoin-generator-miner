import unittest
from bitcoin_wallet_generator.generate_wallet import generate_private_key, private_key_to_wif, private_key_to_public_key, public_key_to_address

class TestBitcoinWallet(unittest.TestCase):
    def test_private_key_length(self):
        pk = generate_private_key()
        self.assertEqual(len(pk), 32)

    def test_wif_format(self):
        pk = generate_private_key()
        wif = private_key_to_wif(pk)
        # Mainnet uncompressed private keys start with '5'
        self.assertTrue(wif.startswith('5'))
        # Length is typically 51 characters
        self.assertEqual(len(wif), 51)

    def test_address_format(self):
        pk = generate_private_key()
        pub = private_key_to_public_key(pk)
        addr = public_key_to_address(pub)
        # Mainnet P2PKH addresses start with '1'
        self.assertTrue(addr.startswith('1'))
        # Length is typically 26-35 characters
        self.assertTrue(25 < len(addr) < 36)

if __name__ == '__main__':
    unittest.main()
