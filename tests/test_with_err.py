import json
import re

import pytest

from with_err import get_err_strs, with_err


@with_err
def my_json_loads(a: str):
    return json.loads(a)


def my_json_loads2(a: str):
    return my_json_loads3(a)


def my_json_loads3(a: str):
    return json.loads(a)


def test_with_err_success():
    '''
    success.
    '''
    json_loads_e = with_err()(json.loads)

    a = '{"test": 1}'
    the_struct, err = json_loads_e(a)
    assert err is None
    assert the_struct == {'test': 1}


def test_with_err_exception():
    '''
    Exception.
    '''
    json_loads_e = with_err()(json.loads)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
    assert isinstance(err, json.decoder.JSONDecodeError)
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: exception: err_str: {err_str}')

    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'test_with_err.py", line \d+, in test_with_err_exception', err_str)


def test_with_err_re_pattern_error_on_json():
    '''
    Exception.
    '''
    with pytest.raises(json.decoder.JSONDecodeError):
        json_loads_e = with_err(re.PatternError)(json.loads)

        a = '{"test": }'
        json_loads_e(a)


def test_with_err_my_json_loads():
    '''
    decorator.
    '''
    a = '{"test": }'
    the_struct, err = my_json_loads(a)

    assert the_struct is None
    assert err is not None
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: my_json_loads: err_str: {err_str}')

    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'test_with_err.py", line \d+, in test_with_err_my_json_loads', err_str)


def test_with_err_my_json_loads2():
    '''
    multi-layer functions.
    '''
    json_loads_e = with_err(my_json_loads2)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
    assert isinstance(err, json.decoder.JSONDecodeError)
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: my_json_loads2: err_str: {err_str}')

    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_json_loads3', err_str)
    assert re.search(r'test_with_err.py", line \d+, in my_json_loads2', err_str)
    assert re.search(r'test_with_err.py", line \d+, in test_with_err_my_json_loads2', err_str)


def test_with_err_re_search():
    '''
    success.
    '''
    re_search_e = with_err(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'test', a)
    assert err is None
    assert match is not None


def test_with_err_direct_wrapper():
    '''
    re: success.
    '''
    re_search_e = with_err(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'test', a)
    assert err is None
    assert match is not None


def test_with_err_direct_wrapper_err():
    '''
    re: pattern error.
    '''
    re_search_e = with_err(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'[test', a)
    assert isinstance(err, re.PatternError)
    assert match is None


# async test
async def async_fetch_data(endpoint: str) -> dict[str, str]:
    if endpoint == "bad":
        raise ValueError("Failed to reach endpoint")
    return {"status": "ok"}


@pytest.mark.asyncio
async def test_with_err_async_err():
    '''
    test async err
    '''
    async_fetch_data_e = with_err(async_fetch_data)
    res, err = await async_fetch_data_e("bad")

    assert isinstance(err, ValueError)
    assert res is None


@pytest.mark.asyncio
async def test_with_err_async_success():
    '''
    test async err
    '''
    async_fetch_data_e = with_err(async_fetch_data)
    res, err = await async_fetch_data_e("good")

    assert err is None
    assert res == {'status': 'ok'}
