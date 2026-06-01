from queue import Queue
from threading import Event, RLock, Thread
from time import time, sleep
from typing import Callable, Union, Any, Optional


class ConditionCallSpec:
    def __init__(self, condition: Callable[..., Union[bool, tuple[bool, *tuple[Any,...]]]], *condition_args, **condition_kwargs):
        self.condition = condition
        self.condition_args = condition_args if condition_args is not None else ()
        self.condition_kwargs = condition_kwargs if condition_kwargs is not None else {}

    @staticmethod
    def _separate_condition_result(condition_result: Any) -> tuple[bool, *tuple[Any,...]]:
        if isinstance(condition_result, bool):
            return (condition_result,)
        elif isinstance(condition_result, tuple):
            if len(condition_result) > 0 and isinstance(condition_result[0], bool):
                return condition_result
            else:
                return False, *condition_result
        else:
            return False, condition_result

    # noinspection PyTypeChecker
    def _call_with_exception_handling(self) -> tuple[bool, *tuple[Any,...]]:
        try:
            result = self.condition(*self.condition_args, **self.condition_kwargs)
            return self._separate_condition_result(result)
        except Exception as e:
            return False, e

    def call(self, call_lock: Optional[RLock] = None) -> tuple[bool, *tuple[Any,...]]:
        if call_lock:
            with call_lock:
                return self._call_with_exception_handling()
        else:
            return self._call_with_exception_handling()


class WaitResult:
    def __init__(self, wait_time: float, result: bool, *other_return_args):
        self.wait_time = wait_time
        self.result = result
        self.exception: Optional[Exception] = None

        if other_return_args is not None and len(other_return_args) > 0 and isinstance(other_return_args[0], Exception):
            self.exception = other_return_args[0]
            other_return_args = other_return_args[1:] if len(other_return_args) >= 2 else tuple()

        self.other_return_args: tuple = other_return_args if other_return_args else tuple()


def wait_until(
        condition_call_spec: ConditionCallSpec,
        timeout: float,
        check_interval: float = 0.1,
        sleep_wake_event: Optional[Event] = None,
        condition_call_sync_lock: Optional[RLock] = None,

) -> WaitResult:
    """
    Waits until the given condition is True or the timeout is reached.
    :param condition_call_spec: A condition call specificication callable that returns a boolean or a tuple whose first element is a boolean.
    :param timeout: Maximum time to wait in seconds.
    :param check_interval: Time to wait between condition checks in seconds.
    :param sleep_wake_event: An event to signal when to wake up from sleep.
    :param condition_call_sync_lock: A lock to synchronize calls to the condition callable.
    :return: WaitResult object
    """
    start_time = time()
    expected_elapsed_time = 0.0

    # Round timeout to milliseconds
    timeout = round(timeout, 3)

    if timeout <= 0:
        result, *other_return_args = condition_call_spec.call(condition_call_sync_lock)
        return WaitResult(0, result, *other_return_args)

    result = False
    other_return_args = (None,)

    elasped_time = time() - start_time
    while elasped_time < timeout:
        result, *other_return_args = condition_call_spec.call(condition_call_sync_lock)
        elasped_time += time() - start_time

        if result or (elasped_time >= timeout):
            return WaitResult(elasped_time, result, *other_return_args)

        expected_elapsed_time += check_interval
        time_to_sleep = expected_elapsed_time - elasped_time

        if time_to_sleep > 0:
            if sleep_wake_event:
                sleep_wake_event.wait(time_to_sleep)
            else:
                sleep(time_to_sleep)

    # If timeout occured post sleep, check condition one last time and return
    elasped_time += time() - start_time
    result, *other_return_args = condition_call_spec.call(condition_call_sync_lock)
    return WaitResult(elasped_time, result, *other_return_args)


class ConditionWaitSpec:
    def __init__(self, condition_call_spec: ConditionCallSpec, timeout: float, check_interval: float, sleep_wake_event: Optional[Event] = None):
        self.condition_call_spec = condition_call_spec
        self.timeout = timeout
        self.check_interval = check_interval
        self.sleep_wake_event = sleep_wake_event

    def wait_for(self, condition_call_sync_lock: Optional[RLock] = None) -> WaitResult:
        return wait_until(
            self.condition_call_spec,
            self.timeout,
            self.check_interval,
            self.sleep_wake_event,
            condition_call_sync_lock
        )


def wait_for_multiple_conditions(condition_wait_specs: list[ConditionWaitSpec], synchronized_condition_checks: bool = True) -> list[WaitResult]:
    if not condition_wait_specs:
        return []

    condition_call_sync_lock = RLock() if synchronized_condition_checks else None

    results_queue: Queue = Queue()

    def _run(condition_wait_spec: ConditionWaitSpec, index: int):
        results_queue.put((index, condition_wait_spec.wait_for(condition_call_sync_lock)))

    for idx, spec in enumerate(condition_wait_specs):
        thread = Thread(target=_run, args=(spec, idx), name=f'wait-condition-{idx}')
        thread.start()

    # noinspection PyTypeChecker
    ordered_wait_results: list[WaitResult] = [None] * len(condition_wait_specs)
    for _ in range(len(condition_wait_specs)):
        idx, result = results_queue.get()
        ordered_wait_results[idx] = result

    return ordered_wait_results
