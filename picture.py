import math
import numpy
from PIL import Image
from PIL import ImageChops
from random import choice
from binascii import b2a_hex, a2b_hex


class Picture(object):
    def __init__(self, path_to_image, secret=None, num_of_bits=1, auto_detect=False):
        self.path_to_image = path_to_image
        self.secret = secret
        self.image = Image.open(path_to_image)
        self.max_image_size = self.image.size[1] * self.image.size[0]
        self.img_width = self.image.size[1]
        self.img_height = self.image.size[0]
        self.BUFFER = b'BUFFER'
        self.number_of_bits = num_of_bits
        if auto_detect:
            self.evaluate_space()

    def evaluate_space(self):
        if self.max_image_size * 3 * self.number_of_bits <= \
                (len(self.secret.encode("UTF-8")) * 8) + (len(self.BUFFER) * 8):
            self.number_of_bits = ((len(self.secret.encode("UTF-8")) * 8) +
                                   (len(self.BUFFER) * 8)) / self.max_image_size * 3
            if self.number_of_bits > 7:
                raise Exception("Could not hide the message! Secret is too large!")
        print("INFO: Using %s bits to hide the secret" % self.number_of_bits)
    ''' 
    b2a_hex:
    Vrátí hexadecimální reprezentaci binárních dat. 
    Každý bajt dat je převeden na odpovídající dvoumístné hexové zobrazení. 
    Objekt vrácených bajtů je tedy dvakrát delší než délka dat
    a2b_hex:
    Vrátí binární data reprezentovaná hexadecimálním řetězcem hexstr. Tato funkce je inverzní k b2a_hex (). 
    hexstr musí obsahovat sudý počet hexadecimálních číslic (což může být velká nebo malá písmena), 
    jinak je vyvolána chyba Error.
    '''

    @staticmethod
    def set_bit(byte_b, bit, position):
        tmp = list(bin(byte_b))
        zeroes = len(tmp) - 2
        if len(tmp) < 10:
            for i in range(0, (8 - zeroes)):
                tmp.insert(tmp.index('b') + 1, '0')
        tmp[-position] = bit
        return int(''.join(tmp), 2)

    def extract_bits(self, color):
        bits = ''
        for bit in range(1, self.number_of_bits + 1):
            tmp = bin(color).replace("0b", '')
            for i in range(0, (8 - len(tmp))):
                tmp = '0' + tmp
            bits += tmp[-bit]
        return bits

    def get_secret(self, raw_bits):
        try:
            bits = [raw_bits[i:i + 7] for i in range(0, len(raw_bits), 7)]
            char = ''
            for bit in bits:
                char += chr(int(bit, 2))
                if self.BUFFER.hex() in char:
                    break
            if len(char) % 2 != 0:
                char += 'A'
            as_ascii = a2b_hex(char.encode('ascii'))
            buffer = as_ascii.find(self.BUFFER)
        except Exception as e:

            raise Exception(str(e))

        if buffer != -1:
            secret = as_ascii[:buffer]
        else:
            raise Exception('Failed to find message buffer...')

        if buffer != -1:
            print("Secret found in the picture: %s" % secret.decode("UTF-8"))

    def create_bitstream(self):
        try:
            text = b'%s' % self.secret.encode("UTF-8")
            text += self.BUFFER

            hex_text = b2a_hex(text).decode('ascii')
            bits = ''
            for char in hex_text:
                tmp = bin(ord(char))[2:]
                if len(tmp) < 7:
                    for i in range(0, (7 - len(tmp))):
                        tmp = '0' + tmp
                bits += tmp
            for i in range(0, ((self.max_image_size * 3 * self.number_of_bits) - len(bits)), 7):
                bits += str(bin(ord(choice('abcdef')))[2:])
            return bits
        except Exception as e:
            raise Exception('Text to binary conversion failed! %s' % str(e))

    def hide_secret(self):
        if self.secret is None:
            raise Exception("Could not hide the message! Secret can't be %s" % self.secret)
        if self.max_image_size * 3 * self.number_of_bits <= \
                (len(self.secret.encode("UTF-8")) * 8) + (len(self.BUFFER) * 8):
            raise Exception('Message is too large!')

        bitstream = iter(self.create_bitstream())

        new_image = Image.new("RGB", (self.img_height, self.img_width), "white")
        try:
            for row in range(self.img_width):
                for col in range(self.img_height):
                    r, g, b = self.image.getpixel((col, row))
                    try:
                        for i in range(1, self.number_of_bits + 1):
                            next_bit = next(bitstream)
                            r = Picture.set_bit(r, next_bit, i)
                        for i in range(1, self.number_of_bits + 1):
                            next_bit = next(bitstream)
                            g = Picture.set_bit(g, next_bit, i)
                        for i in range(1, self.number_of_bits + 1):
                            next_bit = next(bitstream)
                            b = Picture.set_bit(b, next_bit, i)
                    except StopIteration:
                        pass
                    new_image.putpixel((col, row), (r, g, b))
            new_image.save(self.path_to_image.replace(".png", "_secret.png"))
        except Exception as e:
            raise Exception('Could not create a new file with a payload! %s' % str(e))

    def extract_secret(self):
        hidden = ''
        try:
            for row in range(self.image.size[1]):
                for col in range(self.image.size[0]):
                    r, g, b = self.image.getpixel((col, row))
                    hidden += self.extract_bits(r)
                    hidden += self.extract_bits(g)
                    hidden += self.extract_bits(b)
            try:
                self.get_secret(hidden)
                return True
            except Exception as e:
                raise Exception('Failed to extract message: %s' % str(e))
        except Exception as e:
            raise Exception('Failed to extract message: %s' % str(e))

    @staticmethod
    def compare_pictures(file_path1, file_path2):
        try:
            im1 = Image.open(file_path1)
            im2 = Image.open(file_path2)
        except Exception as e:
            raise Exception('Failed to open images: %s' % str(e))
        errors = numpy.asarray(ImageChops.difference(im1, im2)) / 255
        print("Root mean square is: %s" % math.sqrt(numpy.mean(numpy.square(errors))))
