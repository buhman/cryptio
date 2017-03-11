import pytest

from cryptio.header import CryptHeader


iv_length = 12
tag_length = 16
header_length = iv_length + tag_length

test_file = 'test'


@pytest.fixture
def header(fs):
    with open(test_file, 'wb+') as f:
        yield CryptHeader(f)


def test_header_initialize(header):
    header.initialize()
    iv1 = header.iv
    header.initialize()
    iv2 = header.iv

    assert iv1 is not None
    assert iv2 is not None

    assert len(iv1) == iv_length
    assert len(iv2) == iv_length

    assert header._file.tell() == header_length


def test_header_write(header):
    with pytest.raises(AssertionError):
        # no iv or tag
        header.write()

    header.iv = bytes()
    header.tag = bytes()

    with pytest.raises(AssertionError):
        # invalid iv and tag
        header.write()

    header.iv = b'\x01' * iv_length
    tag = b'\x02' * tag_length
    header.write(tag)

    assert header.tag == tag

    header._file.seek(0)
    data = header._file.read()

    assert data[:iv_length] == header.iv
    assert data[iv_length:header_length] == header.tag


def test_header_read(header):
    iv = b'\x01' * iv_length
    tag = b'\x02' * tag_length

    header._file.seek(0)
    header._file.write(iv + tag)

    header.read()

    assert header.iv == iv
    assert header.tag == tag
