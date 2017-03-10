aeadfiles: authenticated file encryption library
================================================

aeadfiles provides a file-like interface for authenticated encryption.

.. _cryptography: https://cryptography.io/en/latest/


Features
--------

- Uses AES-GCM for data integrity validation
- Automatic GCM initialization vector and authentication tag storage
- cryptography_ primitives

Library Installation
--------------------

.. code-block:: bash

   $ pip install aeadfiles

Getting Started
---------------

Example::

    import os
    import aeadfiles

    key = os.urandom(32)

    data = b'binary data'

    with aeadfiles.open('test', 'wb') as f:
        f.write(data)

    with aeadfiles.open('test', 'wb') as f:
        assert f.read() == data

Contents
--------

.. toctree::
   :maxdepth: 2

   api
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
