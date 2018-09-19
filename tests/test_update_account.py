import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')

# Logged out
def test_user_get_validation_error_when_updating_an_account_while_being_logged_out():
    r = TestUtils.update_account(
        uuid='6166a825-00be-4f5c-837c-7d1a1ffc015e',
        email='random555@example.com',
        username='random555',
        password='blabla12345'
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_updating_an_account_with_missing_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_account(
        email='random555@example.com',
        username='random555',
        password='blabla12345'
    )
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


# Invalid Fields
