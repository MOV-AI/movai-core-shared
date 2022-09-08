from movai_core_shared.core.securepassword import SecurePassword
from movai_core_shared.core.secure import generate_secret_string
import unittest


TEST_KEY = generate_secret_string()
class HashPasswordTester(unittest.TestCase):

    def setUp(self) -> None:
        super().__init__()
        self.secure = SecurePassword(TEST_KEY)
        self.init_passwords()

    def init_passwords(self) -> None:
        self.passwords = []
        for i in range(2):
            password = generate_secret_string()
            pair = {'pass': password,
                    'hash': self.secure.create_salted_hash(password)}
            self.passwords.append(pair)

    def test_verify_password(self) -> int:
        self.assertTrue(self.secure.verify_password(self.passwords[0]['pass'],
                                                  self.passwords[0]['hash']))
        self.assertFalse(self.secure.verify_password(self.passwords[0]['pass'],
                                                   self.passwords[1]['hash']))


class EncryptedPasswords(unittest.TestCase):

    def setUp(self) -> None:
        super().__init__()
        self.cipher = SecurePassword(TEST_KEY)
        self.password = generate_secret_string()
        self.cipher_text = self.cipher.encrypt_password(self.password)
        self.plain_text = self.cipher.decrypt_password(self.cipher_text)

    def test_encrypt_password(self):
        self.assertTrue(isinstance(self.cipher_text, bytes),
                        "cipher text in wrong format")
        self.assertNotEqual(self.cipher_text, self.password,
                            "the password is not encrypted")

    def test_decrypt_password(self):
        self.assertTrue(isinstance(self.plain_text, str),
                        "Error: plain text is not in str format")
        self.assertEqual(self.plain_text, self.password,
                         "plain text and original password do not match")


if __name__ == '__main__':
    unittest.main()
