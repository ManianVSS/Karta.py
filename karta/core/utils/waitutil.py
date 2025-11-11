from time import time, sleep
from typing import Callable, Union


def wait_until(
        condition: Callable[..., Union[bool, tuple[bool, ...]]],
        timeout: float,
        check_interval: float = 0.1,
        *condition_args,
        **condition_kwargs,
) -> Union[bool, tuple[bool, ...]]:
    """
    Waits until the given condition is True or the timeout is reached.
    :param condition: A callable that returns a boolean or a tuple whose first element is a boolean.
    :param timeout: Maximum time to wait in seconds.
    :param check_interval: Time to wait between condition checks in seconds.
    :param condition_args: Positional arguments to pass to the condition callable.
    :param condition_kwargs: Keyword arguments to pass to the condition callable.
    :return: The result of the condition callable when it returns True, or the last result before timeout.
    """
    start_time = time()
    expected_elapsed_time = 0.0

    if timeout <= 0:
        return condition(*condition_args, **condition_kwargs)

    condition_outcome = None
    while time() - start_time < timeout:
        condition_outcome = condition(*condition_args, **condition_kwargs)
        condition_result = (isinstance(condition_outcome, bool) and condition_outcome) or (
                isinstance(condition_outcome, tuple) and len(condition_outcome) > 0 and condition_outcome[0])
        if condition_result:
            return condition_outcome
        elapsed_time = time() - start_time
        expected_elapsed_time += check_interval
        time_to_sleep = expected_elapsed_time - elapsed_time
        if time_to_sleep > 0:
            sleep(check_interval)

    return condition_outcome if condition_outcome is not None else condition(*condition_args, **condition_kwargs)
