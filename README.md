# Pystego
Pystego is a Python tool for hiding, unhiding and detect messages in audio and image files using the Least Significant Bit (LSB) technique. 

Supported file formats: png, wav.

Supported encryption/decryption algorithms: AES, ECC.

### Requirements
python modules (all modules are available from pip):
* numpy
* padding
* pyelliptic
* crypto
* pillow


## Installation
Clone our repo:

    git clone ...
    cd mkri-steganography

### Install required packages:

install the requirements:

    python3 setup.py build
    python3 setup.py install


## Usage
### Hide secret:

    python3 pystego.py -f <file> -s <secret>
    python3 pystego.py -f "path-to-file" -s "secret" -b2 "number-of-bits-to-hide-secret-in"

### Unhide secret:

    python3 pystego.py -f <file> 

## Optional Usage

### Help:

    python3 pystego.py --help

    optional arguments:
    -h  --help          show this help message and exit
    -f  --file          FILE,       -f dusk.png (target file)
    -c  --compare       FILE2,      -c FILE2
    -s  --secret        SECRET      -s <file_or_string>
    -i  --investigate   Returns audio info and capacity
    -a  --algorithm     ALGORITHM   -a Choose algorithm (aes, ecc)
    -d  --detect        Detect steganography method
    -b  --bits          Number of bits in which the secret will be stored

    

## Audio 
### Detection of hidden secret:

    python3 pystego.py -f <file> -d

### Choose cryptographic algorithm:

    AES: python3 pystego.py -f <file> -s <secret> -a aes
    ECC: python3 pystego.py -f <file> -s <secret> -a ecc
    
### Audio info and capacity:

    python3 pystego.py -f <file> -i
    
### Example:

Find audio info and capacity:

    python3 pystego.py -f 'summer.wav' -i
    Number of channels (mono/stereo): 2
    Sampling frequency: 44100 Hz
    Number of audio frames: 1323000
    Sample width in bytes: 2
    Available kB: 322.998046875

Encrypt secret with AES:

    python3 pystego.py -f summer.wav -s "my secret message" -a aes
    Passphrase? mypassphrase
    Ciphertext: 6d160c0cc8795babadfef9ebdf9d3761
    Secret was successfully hidden! LSB: 1. Destination file: summer_secret.wav.

Detect secret in target file:

    python3 pystego.py -f 'summer_secret.wav' -d
    Hidden secret was detect in target file. Detected from 1 LSB bits.

Unhide encrypted secret, passphrase is needed for decrypt: 

    python3 pystego.py -f 'summer_secret.wav' -a aes
    Buffer found!
    Hidden secret was successfully recovered from target file.
    Hidden secret: 6d160c0cc8795babadfef9ebdf9d3761
    Passphrase? mypassphrase
    Decrypted secret: my secret message

## Image    
### Number of LSB bits:

By default is used only the last bit.

    python3 pystego.py -f <file> -b
    
### Image comparation:

    python3 pystego.py -f <file> -c <file2>    
    
### Example:    
    
Hide message in last two bits for image:

    python3 pystego.py -f files/lena.png -s HelloWorld -b2

Compare two images:

    python3 pystego.py -f  'lena.png' -c 'lena_secret.png'
    Root mean square is: 0.0027747689759112437

Get secret from the image:

    python3 pystego.py -f files/lena_secret.png -b2

   
    
