#!/usr/bin/python3

import pyelliptic
from hashlib import md5
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
from base64 import b64encode, b64decode
import Padding


class Crypto(object):

    @staticmethod
    def aes_encrypt(plaintext):
        """
        Encrypts secret by AES 256bit ECB

        :param plaintext: string to encrypt
        :return: string cipher
        """
        passphrase = input('Passphrase? ')
        passphrase = md5(passphrase.encode('utf8')).hexdigest()  # helps via MD5 to convert pass on 32 bytes string

        # encodes by base64
        plaintext = b64encode(plaintext.encode())

        # appends padding for default size
        plaintext = Padding.appendPadding(plaintext.decode(), AES.block_size, mode='CMS')

        cipher = AES.new(passphrase, AES.MODE_ECB)

        return hexlify(cipher.encrypt(plaintext)).decode()

    @staticmethod
    def aes_decrypt(ciphertext):
        """
        Decrypts secret by AES 256bit ECB

        :param ciphertext: string cipher to decrypt
        :return: string plaintext
        """
        passphrase = input('Passphrase? ')
        passphrase = md5(passphrase.encode('utf8')).hexdigest()  # helps via MD5 to convert on 32 bytes string
        ciphertext = unhexlify(ciphertext.encode())
        cipher = AES.new(passphrase, AES.MODE_ECB)
        # decrypts cipher
        plaintext = cipher.decrypt(ciphertext).decode('utf-8')
        # removes padding
        plaintext = Padding.removePadding(plaintext, AES.block_size, mode='CMS')
        # decodes plaintext
        plaintext = b64decode(plaintext.encode())

        return plaintext.decode()

    @staticmethod
    def ecc_encrypt(plaintext):
        """
        Encrypts secret by ECC

        :param plaintext: string to encrypt
        :return: hex string of public key, cipher
        """

        plaintext = plaintext.encode()
        ecc_object = pyelliptic.ECC(curve='secp384r1')
        cipher = hexlify(ecc_object.encrypt(plaintext, ecc_object.get_pubkey(), ephemcurve='secp384r1')).decode()
        pub_key = hexlify(ecc_object.get_pubkey()).decode()
        priv_key = hexlify(ecc_object.get_privkey()).decode()

        print('Public key: {}'.format(pub_key))
        print('Private key: {}'.format(priv_key))

        if input('Save private key? ') == 'y':
            f = open("privatekey.txt", "w")
            f.write(priv_key)
            f.close()

        return pub_key, cipher

    @staticmethod
    def ecc_decrypt(pub_key, ciphertext):
        """
        Decrypts secret by ECC

        :param pub_key: string public key
        :param ciphertext: string ciphertext
        :return: string plaintext
        """

        pub_key = unhexlify(pub_key.encode())
        ciphertext = unhexlify(ciphertext.encode())

        priv_key = input('Private? ')
        priv_key = bytes.fromhex(priv_key)
        ecc_object = pyelliptic.ECC(pubkey=pub_key, privkey=priv_key, curve='secp384r1')
        plaintext = ecc_object.decrypt(ciphertext).decode()

        return plaintext
