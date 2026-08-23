import traceback


def get_err_strs(err: Exception | None) -> list[str]:
    """Accepts an exception instance and returns the full traceback as list[str]."""
    if err is None:
        return []

    return traceback.format_exception(err)
