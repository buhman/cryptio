.. _disk-format:

Disk Format
===========

Header
------

The cryptio header starts at the beginning of the encrypted file, and
contains two fields: a 12-byte initialization vector, and a 16-byte
GCM authentication tag:

.. code:: C

   struct {
       uint8 iv[12];
       uint8 tag[16];
   } CryptIOHeader;

The total size of this header is 28 bytes. Immediately following the
header is the ciphertext data.

Overhead
--------

Other than the 28-byte header, the AES-GCM mode introduces no
additional overhead. Writing a 1024-byte plaintext with cryptio will
result in a 1052-byte file.
