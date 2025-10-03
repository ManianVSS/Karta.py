from typing import Callable


def wrap_function_before(function_to_wrap: Callable, before_function: Callable, *args, **kwargs) -> Callable:
    def wrapped_function(*wf_args, **wf_kwargs):
        before_function(*args, **kwargs)
        to_return = function_to_wrap(*wf_args, **wf_kwargs)
        return to_return

    return wrapped_function
