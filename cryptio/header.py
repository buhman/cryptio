import logging
import os
from base64 import urlsafe_b64encode


class CryptHeader:
    _iv_length = 12  # 96 bits
    _tag_length = 16  # 128 bits

    def __init__(self, _file):
        self._file = _file
        self._pos = _file.tell()

        self.iv = None
        self.tag = None

    def initialize(self):
        header_length = self._iv_length + self._tag_length

        self._file.seek(self._pos + header_length)
        self.iv = os.urandom(self._iv_length)

    def write(self, tag=None):
        if tag:
            self.tag = tag

        assert self.iv is not None and len(self.iv) == self._iv_length
        assert self.tag is not None and len(self.tag) == self._tag_length

        self._file.seek(self._pos)
        self._file.write(self.iv)
        self._file.write(self.tag)

        logging.debug('write iv: {}'.format(urlsafe_b64encode(self.iv)))
        logging.debug('write tag: {}'.format(urlsafe_b64encode(self.tag)))

    def read(self):
        self._file.seek(self._pos)
        self.iv = self._file.read(self._iv_length)
        self.tag = self._file.read(self._tag_length)

        logging.debug('read iv: {}'.format(urlsafe_b64encode(self.iv)))
        logging.debug('read tag: {}'.format(urlsafe_b64encode(self.tag)))
