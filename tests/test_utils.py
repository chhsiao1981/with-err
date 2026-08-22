import json
import re

from with_err import get_err_strs


def test_get_err_strs():
    e_str = ''
    try:
        a = json.loads('{')
        print(f'a: {a}')
    except Exception as e:  # ruff: ignore[blind-except]
        e_strs = get_err_strs(e)
        e_str = '\n'.join(e_strs)

    assert e_str != ''
    assert re.search(r'json/__init__.py", line \d+, in loads', e_str)


def test_get_err_strs2():
    e_strs = get_err_strs(None)
    e_str = '\n'.join(e_strs)

    assert e_str == ''
