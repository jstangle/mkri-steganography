import sys
from setuptools import setup, find_packages

VIRTUAL_ENV = hasattr(sys, 'real_prefix')


if __name__ == '__main__':
    setup(name='pystego',
          description='Steganography tool. Written by group number 3, BUT FEEC, MKRI project, 2019',
          version="0.1.0",
          packages=find_packages(),
          author='Jan Stangler',
          install_requires=['padding', 'crypto', 'pyelliptic==1.5.7', 'Pillow', 'numpy']
          )
