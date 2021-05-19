"""Small retry callable in case of specific error occured"""

from datetime import datetime, timedelta
from time import sleep

from pytest_postgresql.compat import psycopg2


def retry(func, timeout: int = 60, possible_exception=Exception):
    """
    Attempt to retry the function for timeout time.

    Most often used for connecting to postgresql database as,
    especially on macos on github-actions, first few tries fails
    with this message:

    ... ::
        FATAL:  the database system is starting up
    """
    time: datetime = datetime.utcnow()
    timeout_diff: timedelta = timedelta(seconds=timeout)
    i = 0
    while True:
        i += 1
        try:
            res = func()
            return res
        except possible_exception as e:
            if time + timeout_diff < datetime.utcnow():
                raise TimeoutError(f"Faile after {i} attempts") from e
            sleep(1)
            pass
