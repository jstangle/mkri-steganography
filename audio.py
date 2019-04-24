#!/usr/bin/python3

import os
import math
import wave
import numpy
import random
import string
from math import ceil
from chunk import Chunk


class Audio(object):
    """
    The steganography class working with audio file in WAV format.

    """
    @staticmethod
    def get_file_capacity(file_path, lsb_bits=1):
        """
        Returns file capacity, depends on number of lsb bits.
        :return:
        """

        # input audio parameters
        audio = wave.open(file_path)
        channel_count = audio.getnchannels()
        frame_count = audio.getnframes()
        sample_width = audio.getsampwidth()
        sample_count = frame_count * channel_count

        # wave doesn't support more than 2 channels
        if sample_width not in range(1, 3):
            raise ValueError('Sample width must be 1 or 2!')

        # max available space
        max_bytes = (sample_count * lsb_bits) / 8
        print('Available kB: ' + str(max_bytes / 1024))

        return max_bytes

    @staticmethod
    def get_chunk(file_path):
        file = open(file_path, 'rb')
        chunk = Chunk(file, bigendian=0)  # https://docs.python.org/3/library/chunk.html
        chunk_name = chunk.getname()  # Chunk ID
        chunk_size = chunk.chunksize  # Chunk velikost (celkem), btw. rozdil s data chunk je 128 bitů...
        print('Chunk ID: ' + str(chunk_name))
        print('Chunk size: ' + str(chunk_size))

    @staticmethod
    def get_info(file_path):
        audio_file = wave.open(file_path, mode='rb')
        # print('Params: ' + str(audio_file.getparams()))
        print('Number of channels (mono/stereo): ' + str(audio_file.getnchannels()))  # pocet kanalu
        print('Sampling frequency: ' + str(audio_file.getframerate()) + ' Hz')
        print('Number of audio frames: ' + str(audio_file.getnframes()))
        print('Sample width in bytes: ' + str(audio_file.getsampwidth()))

    @staticmethod
    def get_spreading_factor(file_path):
        """
        Returns file capacity, depends on used method.
        :return:
        """
        file_size = os.path.getsize(file_path)
        audio_file = wave.open(file_path, 'r')
        frames_number = audio_file.getnframes()

        return frames_number / file_size

    @staticmethod
    def random_string(length=10):
        """
        Generate a random string of fixed length.

        """
        letters_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_digits) for i in range(length))

    @staticmethod
    def hide_data(secret, input_file, output_file=None, lsb_bits=1):
        """
        Hide secret in audio. Creates copy of file with specific file extension.

        :param secret: string data to hide
        :param input_file: the file for hiding secret
        :param output_file: output file path, *_secret.wav by default
        :param lsb_bits: number of lsb bits to use
        """

        buffer = '2qlmRnoPQkreX45Qmt93dr86AfAG68Awd78'

        if not output_file:
            output_file = str(input_file).replace('.wav', '_secret.wav')

        # input audio parameters
        audio = wave.open(input_file)
        channel_count = audio.getnchannels()
        frame_count = audio.getnframes()
        sample_width = audio.getsampwidth()
        sample_count = frame_count * channel_count
        audio_frames = audio.readframes(frame_count)

        # wave doesn't support more than 2 channels
        if sample_width not in range(1, 3):
            raise ValueError('Sample width must be 1 or 2!')
        if lsb_bits > 8:
            raise ValueError('You cannot use more than 8 LSB!')

        # max available bytes for defined lsb_bits
        max_bytes = (sample_count * lsb_bits) // 8

        # data - secret, cipher, buffers
        secret_bytes_size = len(buffer) + len(secret) + len(buffer)

        if max_bytes < secret_bytes_size:
            required_bits = math.ceil(secret_bytes_size * 8 / sample_count)
            if required_bits > 8:
                raise ValueError('File capacity is not sufficient!')
            lsb_bits = required_bits
            max_bytes = (sample_count * lsb_bits) / 8
            print('Target is too small to hide data! It requires at least {} LSB bits. Current file offers {} kB only. '
                  'Increasing number of LSB bits to {}, available space {} kB'.format(str(required_bits),
                                                                                      str(max_bytes / 1024),
                                                                                      str(required_bits),
                                                                                      str(max_bytes / 1024)))
        rest_space = int(max_bytes - secret_bytes_size)

        # append start_buffer and end_buffer, add random salt to the end
        secret_string = buffer + secret + buffer + Audio.random_string(rest_space)
        secret_bytes = secret_string.encode()
        secret_bit_size = len(secret_bytes) * 8
        secret_byte_size = int(ceil(len(secret_bytes) / lsb_bits)) * lsb_bits  # Rounded up

        secret_bits = numpy.zeros(shape=(secret_byte_size, 8), dtype=numpy.uint8)
        secret_bits[:secret_byte_size, :] = numpy\
            .unpackbits(numpy.frombuffer(secret_bytes, dtype=numpy.uint8, count=secret_byte_size))\
            .reshape(secret_byte_size, 8)

        if sample_width == 1:
            audio_dtype = numpy.uint8
        else:
            audio_dtype = numpy.uint16

        bit_height = int(ceil(secret_bit_size / lsb_bits))  # Number of used LSB bits

        audio_bits = numpy.unpackbits(numpy.frombuffer(audio_frames, dtype=audio_dtype,
                                                       count=bit_height).view(numpy.uint8)).reshape(bit_height,
                                                                                                    8 * sample_width)
        audio_bits[:, 8 - lsb_bits:8] = secret_bits.reshape(bit_height, lsb_bits)

        stego = numpy.packbits(audio_bits).tobytes()

        # modified bytes
        stego_audio = wave.open(output_file, "w")
        stego_audio.setparams(audio.getparams())
        stego_audio.writeframes(stego)
        stego_audio.close()

        print('Secret was successfully hidden! LSB: {}. Destination file: {}.'.format(str(lsb_bits), str(output_file)))

    @staticmethod
    def recover_data(input_file, lsb_bits=1):
        """
        Recover data from the file at input_file

        :param input_file: the file with hidden secret
        :param lsb_bits: the number of used lsb bits
        :return: secret
        """

        buffer = '2qlmRnoPQkreX45Qmt93dr86AfAG68Awd78'

        # input stego audio parameters
        stego_audio = wave.open(input_file)
        frame_count = stego_audio.getnframes()
        channel_count = stego_audio.getnchannels()
        sample_width = stego_audio.getsampwidth()
        sample_count = frame_count * channel_count
        audio_frames = stego_audio.readframes(frame_count)

        # wave doesn't support more than 2 channels
        if sample_width not in range(1, 3):
            raise ValueError('Sample width must be 1 or 2!')

        # max possible LSB bits
        max_bits = sample_count * lsb_bits
        max_secret_bits = int(ceil(max_bits / lsb_bits))

        if sample_width == 1:
            audio_dtype = numpy.uint8
        else:
            audio_dtype = numpy.uint16

        secret_bits = numpy.unpackbits(
            numpy.frombuffer(audio_frames, dtype=audio_dtype, count=max_secret_bits).view(numpy.uint8)
        ).reshape(max_secret_bits, 8 * sample_width)[:, 8 - lsb_bits:8]

        output = numpy.packbits(secret_bits).tobytes()[:max_secret_bits // 8]

        if buffer in str(output):
            print('Buffer found!')
            output_string = str(output)
            byte_buffer, secret, byte_buffer = output_string.split(buffer)
            print('Hidden secret was successfully recovered from target file.')
            print('Hidden secret: {}'.format(secret))
            return secret
        else:
            raise ValueError('This file doesn\'t contain any hidden secret!')

    @staticmethod
    def detect_data(input_file):
        """
        Detect Recover data from the file at input_file

        :param input_file: the file with hidden secret
        :return: boolean if exist or not
        """

        buffer = '2qlmRnoPQkreX45Qmt93dr86AfAG68Awd78'

        # input stego audio parameters
        stego_audio = wave.open(input_file)
        frame_count = stego_audio.getnframes()
        channel_count = stego_audio.getnchannels()
        sample_width = stego_audio.getsampwidth()
        sample_count = frame_count * channel_count
        audio_frames = stego_audio.readframes(frame_count)

        # wave doesn't support more than 2 channels
        if sample_width not in range(1, 3):
            raise ValueError('Sample width must be 1 or 2!')

        if sample_width == 1:
            audio_dtype = numpy.uint8
        else:
            audio_dtype = numpy.uint16

        for lsb_bits in range(1, 9):
            # max possible lsb bits
            max_bits = sample_count * lsb_bits
            max_secret_bits = int(ceil(max_bits / lsb_bits))

            secret_bits = numpy.unpackbits(
                numpy.frombuffer(audio_frames, dtype=audio_dtype, count=max_secret_bits).view(numpy.uint8)
            ).reshape(max_secret_bits, 8 * sample_width)[:, 8 - lsb_bits:8]

            output = numpy.packbits(secret_bits).tobytes()[:max_secret_bits // 8]

            if buffer in str(output):
                print('Hidden secret was detect in target file. Detected from {} LSBs.'.format(str(lsb_bits)))
                return True
        print('Nothing found!')
        return False
