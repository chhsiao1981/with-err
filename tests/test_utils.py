import json
import re

from with_err import (
    get_err_strs,
    get_errs,
    get_first_err,
    get_results,
    get_results_or_none,
    is_all_err,
    is_any_err,
    with_err,
)


def test_get_err_strs():
    e_str = ''
    try:
        a = json.loads('{')
        print(f'a: {a}')
    except Exception as e:
        e_strs = get_err_strs(e)
        e_str = '\n'.join(e_strs)

    assert e_str != ''
    assert re.search(r'json/__init__.py", line \d+, in loads', e_str)


def test_get_err_strs2():
    e_strs = get_err_strs(None)
    e_str = '\n'.join(e_strs)

    assert e_str == ''


@with_err
def my_re_search_e(pattern: str, string: str):
    return re.search(pattern, string)


def test_get_errs():
    strs = ['1', '123', '41234', 'a', 'b', 'c']

    match_strs = [my_re_search_e(r'\d+', each) for each in strs]

    errs = get_errs(match_strs)
    assert len(errs) == 6
    assert errs[0] is None
    assert errs[1] is None
    assert errs[2] is None
    assert errs[3] is None
    assert errs[4] is None
    assert errs[5] is None

    rets = get_results(match_strs)
    assert len(rets) == 6
    assert rets[0] is not None
    assert rets[1] is not None
    assert rets[2] is not None
    assert rets[3] is None
    assert rets[4] is None
    assert rets[5] is None

    the_is_any_err = is_any_err(match_strs)
    assert not the_is_any_err

    the_is_all_err = is_all_err(match_strs)
    assert not the_is_all_err

    first_err = get_first_err(match_strs)
    assert first_err is None


def test_get_errs2():
    strs = ['1', '123', '41234', 'a', 'b', 'c']

    match_strs = [my_re_search_e(r'[0-9', each) for each in strs]

    errs = get_errs(match_strs)
    assert len(errs) == 6
    assert isinstance(errs[0], re.PatternError)
    assert isinstance(errs[1], re.PatternError)
    assert isinstance(errs[2], re.PatternError)
    assert isinstance(errs[3], re.PatternError)
    assert isinstance(errs[4], re.PatternError)
    assert isinstance(errs[5], re.PatternError)

    rets = get_results(match_strs)
    assert len(rets) == 6
    assert rets[0] is None
    assert rets[1] is None
    assert rets[2] is None
    assert rets[3] is None
    assert rets[4] is None
    assert rets[5] is None

    the_is_any_err = is_any_err(match_strs)
    assert the_is_any_err

    the_is_all_err = is_all_err(match_strs)
    assert the_is_all_err

    first_err = get_first_err(match_strs)
    assert isinstance(first_err, re.PatternError)


def test_get_errs3():
    patterns = [r'[0-9', r'\d+', r'\W+', r'\d+\W+', r'[z-a]', r'\d+\W*']

    match_strs = [my_re_search_e(each, '12345') for each in patterns]

    errs = get_errs(match_strs)
    assert len(errs) == 6
    assert isinstance(errs[0], re.PatternError)
    assert errs[1] is None
    assert errs[2] is None
    assert errs[3] is None
    assert isinstance(errs[4], re.PatternError)
    assert errs[5] is None

    rets = get_results(match_strs)
    assert len(rets) == 6
    assert rets[0] is None
    assert rets[1] is not None
    assert rets[2] is None
    assert rets[3] is None
    assert rets[4] is None
    assert rets[5] is not None

    the_is_any_err = is_any_err(match_strs)
    assert the_is_any_err

    the_is_all_err = is_all_err(match_strs)
    assert not the_is_all_err

    first_err = get_first_err(match_strs)
    assert isinstance(first_err, re.PatternError)


def test_get_errs4():
    patterns = r'[0-9', r'\d+', r'\W+', r'\d+\W+', r'[z-a]', r'\d+\W*'

    match_strs = [my_re_search_e(each, '12345') for each in patterns]

    errs = get_errs(match_strs)
    assert len(errs) == 6
    assert isinstance(errs[0], re.PatternError)
    assert errs[1] is None
    assert errs[2] is None
    assert errs[3] is None
    assert isinstance(errs[4], re.PatternError)
    assert errs[5] is None

    rets = get_results(match_strs)
    assert len(rets) == 6
    assert rets[0] is None
    assert rets[1] is not None
    assert rets[2] is None
    assert rets[3] is None
    assert rets[4] is None
    assert rets[5] is not None

    the_is_any_err = is_any_err(match_strs)
    assert the_is_any_err

    the_is_all_err = is_all_err(match_strs)
    assert not the_is_all_err

    first_err = get_first_err(match_strs)
    assert isinstance(first_err, re.PatternError)


def _gen_patterns():
    patterns = r'[0-9', r'\d+', r'\W+', r'\d+\W+', r'[z-a]', r'\d+\W*'
    yield from patterns


def test_get_errs_generator():
    match_strs = [my_re_search_e(each, '12345') for each in _gen_patterns()]

    errs = get_errs(match_strs)
    assert len(errs) == 6
    assert isinstance(errs[0], re.PatternError)
    assert errs[1] is None
    assert errs[2] is None
    assert errs[3] is None
    assert isinstance(errs[4], re.PatternError)
    assert errs[5] is None

    rets = get_results_or_none(match_strs)
    assert len(rets) == 6
    assert rets[0] is None
    assert rets[1] is not None
    assert rets[2] is None
    assert rets[3] is None
    assert rets[4] is None
    assert rets[5] is not None

    the_is_any_err = is_any_err(match_strs)
    assert the_is_any_err

    the_is_all_err = is_all_err(match_strs)
    assert not the_is_all_err

    first_err = get_first_err(match_strs)
    assert isinstance(first_err, re.PatternError)


@with_err
def echo_e(a: str):
    return a


def test_get_results():
    patterns = [r'[0-9', r'\d+', r'\W+', r'\d+\W+', r'[z-a]', r'\d+\W*']

    rets = [echo_e(each) for each in patterns]

    errs = get_errs(rets)
    assert len(errs) == 6
    assert errs[0] is None
    assert errs[1] is None
    assert errs[2] is None
    assert errs[3] is None
    assert errs[4] is None
    assert errs[5] is None

    results = get_results(rets)
    assert len(results) == 6
    assert results[0] == r'[0-9'
    assert results[1] == r'\d+'
    assert results[2] == r'\W+'
    assert results[3] == r'\d+\W+'
    assert results[4] == r'[z-a]'
    assert results[5] == r'\d+\W*'

    the_is_any_err = is_any_err(rets)
    assert not the_is_any_err

    the_is_all_err = is_all_err(rets)
    assert not the_is_all_err

    first_err = get_first_err(rets)
    assert first_err is None
