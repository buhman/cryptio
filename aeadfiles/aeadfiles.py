import builtins
import io
import os

from base64 import urlsafe_b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from memoized_property import memoized_property


def default_cipher(key, iv, tag=None):
    return Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    )


class CryptHeader:
    _iv_length = 12  # 96 bits
    _tag_length = 16  # 128 bits

    def __init__(self, _file):
        self._file = _file
        self._pos = _file.seek(0, io.SEEK_CUR)
        if self._pos is None:
            self._pos = 0

        self.iv = None
        self.tag = None

    def initialize(self):
        header_length = self._iv_length + self._tag_length

        self._file.seek(self._pos + header_length)
        self.iv = os.urandom(self._iv_length)

    def write(self, tag=None):
        if tag:
            self.tag = tag

        assert len(self.iv) == self._iv_length
        assert len(self.tag) == self._tag_length

        self._file.seek(self._pos)
        self._file.write(self.iv)
        self._file.write(self.tag)

        print('write iv: {}'.format(urlsafe_b64encode(self.iv)))
        print('write tag: {}'.format(urlsafe_b64encode(self.tag)))

    def read(self):
        self._file.seek(self._pos)
        self.iv = self._file.read(self._iv_length)
        self.tag = self._file.read(self._tag_length)

        print('read iv: {}'.format(urlsafe_b64encode(self.iv)))
        print('read tag: {}'.format(urlsafe_b64encode(self.tag)))


class CryptWriter:
    def __init__(self, header, key):
        self.header = header
        self.key = key
        self.initialized = False

    @memoized_property
    def encryptor(self):
        assert not self.initialized
        self.header.initialize()
        self.initialized = True
        return default_cipher(self.key, self.header.iv).encryptor()

    def finalize(self):
        if self.initialized:
            self.encryptor.finalize()
            self.header.write(self.encryptor.tag)


class CryptReader:
    def __init__(self, header, key):
        self.header = header
        self.key = key
        self.initialized = False

    @memoized_property
    def decryptor(self):
        assert not self.initialized
        self.header.read()
        self.initialized = True
        return default_cipher(self.key, self.header.iv,
                              self.header.tag).decryptor()

    def finalize(self):
        if self.initialized:
            self.decryptor.finalize()


class CryptIOBase(io.RawIOBase):
    def __init__(self, _file, key):
        self._file = _file

        self.iv = None

        header = CryptHeader(_file)
        self.reader = CryptReader(header, key)
        self.writer = CryptWriter(header, key)

    def read(self, size=-1):
        decryptor = self.reader.decryptor

        chunk = self._file.read(size)
        print('read aes', chunk)

        return decryptor.update(chunk)

    def write(self, chunk):
        encryptor = self.writer.encryptor

        chunk = encryptor.update(chunk)
        print('write aes', chunk)

        return self._file.write(chunk)

    def close(self):
        self.writer.finalize()
        self.reader.finalize()

        return self._file.close()


def open(filename, *, key, mode='rb', _open=None, **kwargs):
    if not _open:
        _open = builtins.open

    _file = _open(filename, mode=mode, **kwargs)

    return CryptIOBase(_file, key)
