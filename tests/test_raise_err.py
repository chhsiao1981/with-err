import inspect
import json
import os
import re
from dataclasses import dataclass
from typing import Self

import pytest

from with_err import get_err_strs, raise_err, with_err
from with_err.raise_err import _get_parent_frame


@pytest.fixture(scope="module", autouse=True)
def init():
    # setup
    yield
    # teardown


def call_raise_err():
    return my_raise_err()


def my_raise_err():
    frame = _get_parent_frame()
    return frame


def test_get_parent_frame():

    frame = call_raise_err()
    print(f'test_get_parent_frame: filename: {frame.f_code.co_filename} lineno: {frame.f_lineno}')

    assert os.path.basename(frame.f_code.co_filename) == 'test_raise_err.py'
    assert frame.f_code.co_name == "call_raise_err"


def err_json_loads():
    json_loads_e = with_err(json.loads)
    ret, err = json_loads_e('{"test": }')
    return ret, raise_err(err)


def test_raise_err():
    ret, err = err_json_loads()
    err_strs = get_err_strs(err)
    err_str = '\n'.join(err_strs)
    print(f'test_raise_err: err_str: {err_str}')

    assert ret is None
    assert re.search(r'test_raise_err.py", line \d+, in err_json_loads', err_str)
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'json.decoder.JSONDecodeError: Expecting value: line 1 column 10', err_str)


def ok_json_loads():
    json_loads_e = with_err(json.loads)
    ret, err = json_loads_e('{"test": 1}')
    return ret, raise_err(err)


def test_raise_err2():
    ret, err = ok_json_loads()
    assert err is None
    assert ret == {"test": 1}


def mock_currentframe_none():
    return


@pytest.fixture(scope="function")
def mock_currentframe():
    orig_currentframe = inspect.currentframe
    inspect.currentframe = mock_currentframe_none
    # setup
    yield
    inspect.currentframe = orig_currentframe
    # teardown


def test_raise_err_mock_currentframe(mock_currentframe):
    ret, err = err_json_loads()
    err_strs = get_err_strs(err)
    err_str = '\n'.join(err_strs)
    print(f'test_raise_err: err_str: {err_str}')

    assert ret is None
    assert not re.search(r'test_raise_err.py", line \d+, in err_json_loads', err_str)
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'json.decoder.JSONDecodeError: Expecting value: line 1 column 10', err_str)


@dataclass
class MockFrame:
    f_back: Self | None = None


def mock_currentframe_none2():
    return MockFrame()


@pytest.fixture(scope="function")
def mock_currentframe2():
    orig_currentframe = inspect.currentframe
    inspect.currentframe = mock_currentframe_none2
    # setup
    yield
    inspect.currentframe = orig_currentframe
    # teardown


def test_raise_err_mock_currentframe2(mock_currentframe2):
    ret, err = err_json_loads()
    err_strs = get_err_strs(err)
    err_str = '\n'.join(err_strs)
    print(f'test_raise_err: err_str: {err_str}')

    assert ret is None
    assert not re.search(r'test_raise_err.py", line \d+, in err_json_loads', err_str)
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'json.decoder.JSONDecodeError: Expecting value: line 1 column 10', err_str)


def mock_currentframe_none3():
    return MockFrame(f_back=MockFrame(f_back=None))


@pytest.fixture(scope="function")
def mock_currentframe3():
    orig_currentframe = inspect.currentframe
    inspect.currentframe = mock_currentframe_none3
    # setup
    yield
    inspect.currentframe = orig_currentframe
    # teardown


def test_raise_err_mock_currentframe3(mock_currentframe3):
    ret, err = err_json_loads()
    err_strs = get_err_strs(err)
    err_str = '\n'.join(err_strs)
    print(f'test_raise_err: err_str: {err_str}')

    assert ret is None
    assert not re.search(r'test_raise_err.py", line \d+, in err_json_loads', err_str)
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'json.decoder.JSONDecodeError: Expecting value: line 1 column 10', err_str)


count_mock_currentframe_none4 = 0


def mock_currentframe_none4():
    global count_mock_currentframe_none4
    if count_mock_currentframe_none4 == 0:
        count_mock_currentframe_none4 += 1
        return None

    return MockFrame(f_back=MockFrame(f_back=None))


@pytest.fixture(scope="function")
def mock_currentframe4():
    orig_currentframe = inspect.currentframe
    inspect.currentframe = mock_currentframe_none4
    # setup
    yield
    inspect.currentframe = orig_currentframe
    # teardown


def test_raise_err_mock_currentframe4(mock_currentframe4):
    ret, err = err_json_loads()
    err_strs = get_err_strs(err)
    err_str = '\n'.join(err_strs)
    print(f'test_raise_err: err_str: {err_str}')

    assert ret is None
    assert not re.search(r'test_raise_err.py", line \d+, in err_json_loads', err_str)
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'json.decoder.JSONDecodeError: Expecting value: line 1 column 10', err_str)
