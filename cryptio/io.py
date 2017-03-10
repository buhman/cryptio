import builtins
import io

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from memoized_property import memoized_property

from cryptio.header import CryptHeader


def default_cipher(key, iv, tag=None):
    return Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    )


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


class CryptIO(io.RawIOBase):
    """:class:`CryptIO` is a minimal file-like object wrapper that only specifically implements :meth:`read`, :meth:`write`, and :meth:`close`.

    Example::

        chunk = f.read(1024)
        f.write(b'bytes')
        f.close()

    :class:`CryptIO` is also a context manager, and can be used with the `with` statement like a normal :class:`FileIO` object.

    The difference between :class:`FileIO` and :class:`CryptIO`:

    - :meth:`read` and :meth:`write` transparently handle aes-gcm decryption and encryption, respectively.
    - :meth:`close` transparently handles message validation and file header updates
    - initialization vectors and gcm authentication tags are handled automatically
    """

    def __init__(self, _file, key):
        self._file = _file

        self.iv = None

        header = CryptHeader(_file)
        self.reader = CryptReader(header, key)
        self.writer = CryptWriter(header, key)

    def read(self, size=-1):
        """Read a ciphertext chunk from the underlying file object, and decrypt the result.

        :param int size: number of bytes to be read
        :returns: plaintext chunk
        :rtype: bytes
        """
        decryptor = self.reader.decryptor

        chunk = self._file.read(size)
        #logging.debug('read aes: {}'.format(chunk))

        return decryptor.update(chunk)

    def write(self, chunk):
        """Encrypts chunk, and writes the ciphertext to the underlying file object.

        :param bytes chunk: bytes or similar
        :return: number of ciphertext bytes written
        :rtype: int
        """
        encryptor = self.writer.encryptor

        chunk = encryptor.update(chunk)
        #logging.debug('write aes: {}'.format(chunk))

        return self._file.write(chunk)

    def close(self):
        """In addition to closing the underlying file object, also handle any outstanding encryptor or decryptor finalization as necessary.

        :raises InvalidTag: if the GCM tag does not match the ciphertext
        """
        self.writer.finalize()
        self.reader.finalize()

        return self._file.close()


def open(file, mode='rb', *, key, _open=None, **kwargs):
    """:func:`.open` is a wrapper around :func:`io.open`, with a few differences:

    - instead of some variant of an :class:`io.FileIO` object, a :class:`CryptIO` wrapper is returned
    - only binary modes are supported

    Example::

        key = os.urandom(32)  # 16 and 24-byte keys are also valid
        f = open('filename', 'rb', key=key)

    For more information on how to manipulate the object returned by :func:`open`, see :class:`CryptIO`

    :param file: path-like object; see `open <https://docs.python.org/3.6/library/functions.html#open>`_
    :param mode: mode string
    :param key: aes symmetric key
    :return: encrypted file object wrapper
    :rtype: CryptIO
    """
    if not _open:
        _open = builtins.open

    _file = _open(file, mode=mode, **kwargs)

    return CryptIO(_file, key)
