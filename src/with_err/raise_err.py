# https://chatgpt.com/c/6a8b3620-9cb0-83ea-baf6-1ab4a31e473b

import inspect
import types


def raise_err(err: Exception | None):
    '''
    `raise_err` does not raise the exception, but augments traceback with the caller's frame.
    '''
    if err is None:
        return

    parent_frame = _get_parent_frame()
    if parent_frame is None:
        return err

    tb = err.__traceback__

    combined_tb = types.TracebackType(
        tb_next=tb,
        tb_frame=parent_frame,
        tb_lasti=parent_frame.f_lasti,
        tb_lineno=parent_frame.f_lineno,
    )

    return err.with_traceback(combined_tb)


def _get_parent_frame():
    frame = _try_get_currentframe()

    # frame as _get_parent_frame.
    if frame is None:
        return

    # frame.f_back as raise_err
    if frame.f_back is None:
        return

    # framer.f_back.f_back as caller frame of raise_err.
    return frame.f_back.f_back


def _try_get_currentframe():
    frame = inspect.currentframe()
    if frame is not None:  # frame as _try_get_currentframe
        return frame.f_back  # f_back as _get_parent_frame

    # XXX hack for nuitka.
    try:
        raise ValueError('none')
    except ValueError:
        frame = inspect.currentframe()  # frame as _try_get_currentframe
        if frame is None:
            return None
        return frame.f_back  # f_back as _get_parent_frame
