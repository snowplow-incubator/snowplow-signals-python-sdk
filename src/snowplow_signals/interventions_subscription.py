import atexit
from collections.abc import Callable, Generator, Iterable, Iterator
from contextlib import AbstractContextManager, closing
from queue import Empty, Queue
from threading import Event, Thread
from typing import Self

from .api_client import ApiClient
from .models import (
    AttributeKeyIdentifiers,
    InterventionInstance,
)


class InterventionsSubscription(AbstractContextManager, Iterable):
    """
    A subscription for interventions published to the given targets.

    Upon calling `start()`, or use in a `with` statement, requests interventions for the given targets.
    Interventions are buffered locally in a `queue.Queue` until requested via `.get()`, which wraps the queue.
    Callbacks to handle interventions can be registered if you require multiple consumers for a single subscription.
    If you want to use callbacks exclusively and not have buffering, disable it with the `buffer` parameter to not use queuing.
    With buffering enabled, you can iterate over any buffered interventions via iteration.
    Upon exiting the `with` statement or upon calling `stop()`, aborts the request.
    The same subscription can be restarted if required, but not started multiple times concurrently.
    When started, subscription instances are registered in the class-level `InterventionSubscription.instances` set.
    This keeps a reference to the instance to prevent it being garbage collected so it can continue passing interventions to callbacks even when out of scope.
    """

    instances: set[Self] = set()

    def __init__(
        self, api_client: ApiClient, targets: AttributeKeyIdentifiers, buffer=True
    ) -> None:
        self.targets = targets
        self.api_client = api_client
        self._queue: Queue[InterventionInstance] | None = Queue() if buffer else None
        self._close: Event = Event()
        self._handlers: dict[Callable[[InterventionInstance], object], bool] = {}
        self._thread: Thread | None = None

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def __del__(self):
        self.stop()

    @classmethod
    def cleanup(cls):
        cls.instances.clear()

    def __iter__(self) -> Iterator[InterventionInstance]:
        """
        Iterate over any locally buffered interventions, waiting up to .1 seconds for new ones to arrive, and then stop iterating.
        """

        def iterate() -> InterventionInstance | None:
            if self._queue is None:
                raise TypeError("Buffering required to iterate over subscription")
            try:
                return self.get(block=True, timeout=0.1)
            except Empty:
                return None

        return iter(iterate, None)

    def start(self) -> None:
        """
        Send request to the Signals API for interventions, and start a background thread to dispatch them to the local buffer or registered handlers.
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Subscription already running")

        self.instances.add(self)
        self._close.clear()

        stream = self.api_client.make_stream_request(
            method="GET",
            endpoint="interventions",
            params=self.targets.root,
            headers={"Accept": "text/event-stream"},
        )

        self._thread = Thread(
            target=self._pipe,
            name=f"SignalsInterventions-{id(self)}",
            daemon=True,
            args=(stream, self._close),
        )

        self._thread.start()

    def get(self, block=True, timeout=None) -> InterventionInstance:
        """
        Get an already retrieved intervention from the buffer, or block waiting for a new intervention to be retrieved and enter the buffer.
        If buffering is disabled, raises a `TypeError`.

        Args:
            block: If True (the default) block until an intervention is available in the buffer, else only return an already available intervention (or raise `queue.Empty` if none).
            timeout: If `block` is True, wait at most `timeout` seconds before failing with `queue.Empty`; if `None`, wait indefinitely. Ignored if `block` is False.
        """
        if self._queue:
            return self._queue.get(block, timeout)
        else:
            raise TypeError("Buffering required to iterate over subscription")

    def add_handler(
        self, handler: Callable[[InterventionInstance], object], ignore_fail=True
    ) -> None:
        """
        Register a new handler to receive interventions.

        Args:
            handler: The handler function to be added to the subscription.
            ignore_fail: If True, exceptions thrown by the handler will be swallowed.
        """
        self._handlers.setdefault(handler, ignore_fail)

    def remove_handler(self, handler: Callable[[InterventionInstance], object]) -> bool:
        """
        De-register a previously added intervention handler.

        Args:
            handler: The handler function to be removed from the subscription.
        Returns:
            True if the handler was removed; False if the handler was not already registered.
        """
        return self._handlers.pop(handler, None) is not None

    def stop(self) -> None:
        """
        Abort the request to the API that is awaiting new interventions, closing the thread that forwards them to registered handlers or the local buffer.
        """
        self._close.set()
        self.instances.discard(self)

    def _pipe(self, stream: Generator[str | None], closed: Event) -> None:
        with closing(stream):
            for event in stream:
                if closed.is_set():
                    break

                if event and event.startswith("data: "):
                    intervention = InterventionInstance.model_validate_json(
                        event[len("data: ") :]
                    )

                    if self._queue:
                        self._queue.put(intervention)

                    for handler, ignore_fail in self._handlers.items():
                        try:
                            handler(intervention)
                        except Exception:
                            if not ignore_fail:
                                raise
                            continue


atexit.register(InterventionsSubscription.cleanup)
