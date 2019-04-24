#!/usr/bin/python3

import sys
import logging
import argparse

from crypto import Crypto
from audio import Audio
from picture import Picture


class Pystego(object):
    def __init__(self, file_path, secret, algorithm=None, bits=1):
        """
        The constructor function that provides all unnecessary inputs.

        :param file_path: The input file for hiding secret.
        :param secret: The secret to be hidden in file.
        :param algorithm: The encryption algorithm for secret.
        :param bits: The number of LSB

        """

        self.init_logging()
        logging.info('Logging initiated.')

        self.secret = secret
        self.file_path = file_path
        self.algorithm = algorithm

        if not bits:
            self.bits = 1
        else:
            self.bits = int(str(bits))

        try:
            file = open(file_path)
        except Exception as e:
            print("The file {} doesn\'t exist! {}".format(str(file_path), str(e)))
            sys.exit(1)

    @staticmethod
    def init_logging():
        level = logging.INFO
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=level)

    def manage_audio(self):
        """
        Function takes care about Audio, encrypts and decrypts secret.

        """

        if self.algorithm == 'aes':
            if self.secret:
                encrypted_secret = Crypto.aes_encrypt(self.secret)
                print('Ciphertext: {}'.format(str(encrypted_secret)))
                Audio.hide_data(str(encrypted_secret), self.file_path, lsb_bits=self.bits)
            else:
                encrypted_secret = Audio.recover_data(self.file_path, lsb_bits=self.bits)
                decrypted_secret = Crypto.aes_decrypt(encrypted_secret)
                print('Decrypted secret: {}'.format(str(decrypted_secret)))
        elif self.algorithm == 'ecc':
            if self.secret:
                pub_key, encrypted_secret = Crypto.ecc_encrypt(self.secret)
                Audio.hide_data(pub_key + encrypted_secret, self.file_path, lsb_bits=self.bits)
            else:
                cipher = Audio.recover_data(self.file_path, lsb_bits=self.bits)
                pub_key, encrypted_secret = cipher[:194], cipher[194:]
                print('Public key: {}'.format(str(pub_key)))
                print('Ciphertext: {}'.format(str(encrypted_secret)))
                decrypted_secret = Crypto.ecc_decrypt(pub_key, encrypted_secret)

                print('Decrypted secret: {}'.format(str(decrypted_secret)))
        else:
            if self.secret:
                Audio.hide_data(self.secret, self.file_path, lsb_bits=self.bits)
            else:
                Audio.recover_data(self.file_path, lsb_bits=self.bits)  # LSB bits = 1 by default


def main():
    # optional arguments
    parser = argparse.ArgumentParser(usage='$prog [options] -f <file> -s <secret>', description='Steganography tool',
                                     add_help=True, epilog='Steganography tool. Written by group number 3, BUT FEEC, '
                                                           'MKRI project, 2019')
    parser.add_argument('-f', '--file', action='store', dest='file', help='-f dusk.png (target file)', required=True)
    parser.add_argument('-c', '--compare', action='store', dest='file2', help='-f dusk.png (file with the secret)',
                        required=False)
    parser.add_argument('-s', '--secret', action='store', dest='secret', help='-s <file_or_string>', required=False)
    parser.add_argument('-i', '--investigate', action='store_true', dest='investigate',
                        help='-c Returns audio info and capacity', required=False)
    parser.add_argument('-a', '--algorithm', action='store', dest='algorithm', help='-a Choose algorithm (aes, ecc)',
                        required=False)
    parser.add_argument('-d', '--detect', action='store_true', dest='detection', help='-d Detect steganography method',
                        required=False)
    parser.add_argument('-b', '--bits', action='store', dest='bits', help='-b number of bits in which the secret '
                                                                          'will be stored', required=False)
    parser.set_defaults(auto=False)
    args = parser.parse_args()

    # instance of the class Pystego
    pystego = Pystego(args.file, args.secret, args.algorithm, args.bits)
    logging.info('Created pystego instance successfully. Entering decision tree.')

    # decision tree of function calling
    if args.file:
        if args.file2:
            if '.png' in args.file and '.png' in args.file2:
                try:
                    Picture.compare_pictures(args.file, args.file2)
                    sys.exit(0)
                except Exception as e:
                    print("FAIL: Could not compare images: %s" % str(e))
                    sys.exit(1)
        if args.investigate:
            if '.wav' in args.file:
                Audio.get_info(args.file)
                Audio.get_file_capacity(args.file)
        elif args.detection:
            if '.wav' in args.file:
                Audio.detect_data(args.file)
        elif args.secret or not args.secret:
            # hiding or recovering secret from file
            if '.wav' in args.file:
                pystego.manage_audio()
            elif '.png' in args.file:
                if args.secret:
                    try:
                        if args.bits is not None:
                            if 0 < int(args.bits) < 8:
                                Picture(args.file, args.secret, int(args.bits), args.auto).hide_secret()
                        else:
                            print("INFO: Using default value(1) for LSB method.")
                            Picture(args.file, args.secret, auto_detect=args.auto).hide_secret()
                        sys.exit(0)
                    except Exception as e:
                        print(e)
                        sys.exit(1)
                else:
                    try:
                        if args.bits is not None:
                            if 0 < int(args.bits) < 8:
                                Picture(args.file, num_of_bits=int(args.bits)).extract_secret()
                        else:
                            print("INFO: Using default value(1) for LSB method.")
                            Picture(args.file).extract_secret()
                        sys.exit(0)
                    except Exception as e:
                        print(e)
                        sys.exit(1)
            else:
                raise IOError('Unsupported file extension!')
    else:
        raise IOError('File is not specified!')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted... Terminating')
        sys.exit()
