'''Shared pytest fixtures for the test suite.

The tests exercise the real tool and agent code paths, which talk to the
live ``supply_chain`` Postgres database configured in ``.env``. The
``database`` fixture below checks that the database is reachable and skips
any test that depends on it when it is not, so the suite stays green on a
machine without the database rather than reporting spurious failures.
'''

import pytest

from app.db.connection import get_connection


@pytest.fixture(scope='session')
def database():
    '''Confirm the ``supply_chain`` database is reachable, else skip.

    Request this fixture from any test that reads from the database.
    '''

    try:
        conn = get_connection()
    except Exception as exc:  # noqa: BLE001 - any driver error means "unavailable"
        pytest.skip(f'supply_chain database is not reachable: {exc}')

    conn.close()
