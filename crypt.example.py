from Crypto.Cipher import AES
from Crypto.Hash import SHA256

class Crypt(object):
	""" Encrypt / Decrypt password """
	def __init__(self, key='example'):
		super(Crypt, self).__init__()
		self.master_key = self.get_master_key(key)
		
	def get_master_key(self, string):
		key = SHA256.new(string.encode('utf-8'))		
		return key.digest()    

	def encrypt(self, text, pad, num_pad=16):
		cipher = AES.new(self.master_key, AES.MODE_ECB)	
		padding = pad * (num_pad - len(text))	
		text += padding
		cipher = cipher.encrypt(text.encode('utf-8'))
		# print(cipher.hex())
		return cipher.hex()

	def decrypt(self, text, pad):
		text = bytes.fromhex(text)	
		cipher = AES.new(self.master_key, AES.MODE_ECB)	
		cipher = cipher.decrypt(text)
		cipher = cipher.rstrip(pad.encode('utf-8'))
		return cipher.decode('utf-8')

	def teamtoolEncrypt(self, text, sep='-', num_pad=16):	
		sp = text.split(sep)
		encrypted_parts = [self.encrypt('#', num_pad=num_pad) for part in sp]
		return '-'.join(encrypted_parts)

	def teamtoolDecrypt(self, text, sep='-', num_pad=16):
		sp = text.split(sep)
		decrypted_parts = [self.decrypt(part, '#') for part in sp]
		return '-'.join(decrypted_parts)