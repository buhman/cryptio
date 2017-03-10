import os
from base64 import b64encode

import pytest

import cryptio


test_data = [
    b64encode(os.urandom(32)),
    b64encode(os.urandom(32))
]


@pytest.fixture
def key():
    return os.urandom(32)


real_os = os


def test_roundtrip(fs, key):
    def new_open(file_path, *args, **kwargs):
        if file_path == os.devnull:
            return real_os.open(file_path, *args, **kwargs)

        return os.open(file_path, *args, **kwargs)

    # fixme
    os.open = new_open

    with cryptio.open('test', mode='wb', key=key) as f:
        for data in test_data:
            f.write(data)

    assert fs.Exists('test')

    with cryptio.open('test', mode='rb', key=key) as f:
        for data in test_data:
            assert data == f.read(len(data))
