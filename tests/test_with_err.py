import json
import re

from with_err import get_err_strs, with_err


@with_err()
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
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: exception: err_str: {err_str}')

    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'test_with_err.py", line \d+, in test_with_err_exception', err_str)


def test_with_err_JSONDecodeError():
    '''
    specified JSONDecodeError.
    '''
    json_loads_e = with_err(json.decoder.JSONDecodeError)(json.loads)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
    err_str = "\n".join(get_err_strs(err))
    print(f'test_with_err: JSONDecodeError: err_str: {err_str}')

    assert 'json.decoder.JSONDecodeError: Expecting value: line 1 column 10 (char 9)' in err_str
    assert re.search(r'with_err.py", line \d+, in wrapper', err_str)
    assert re.search(r'json/__init__.py", line \d+, in loads', err_str)
    assert re.search(r'test_with_err.py", line \d+, in test_with_err_JSONDecodeError', err_str)


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
    json_loads_e = with_err()(my_json_loads2)

    a = '{"test": }'
    the_struct, err = json_loads_e(a)

    assert the_struct is None
    assert err is not None
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
    re_search_e = with_err()(re.search)

    a = '{"test": 1}'
    match, err = re_search_e(r'test', a)
    assert err is None
    assert match is not None
