import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Logged out
def test_user_doesnt_get_validation_error_when_creating_an_account_while_being_logged_out():
    # 1) Create an account
    r = TestUtils.create_account(
        email='random555@example.com',
        username='random555',
        password='blabla12345'
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    r = TestUtils.login('random555', 'blabla12345')
    assert r.exit_code == 0

    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_an_account_with_missing_email():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_account(
        username='random555',
        password='blabla12345'
    )

    assert r.exit_code == 2
    assert 'Missing option "--email"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


def test_user_get_validation_error_when_creating_an_account_with_missing_username():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_account(
        email='random555@example.com',
        password='blabla12345'
    )
    assert r.exit_code == 2
    assert 'Missing option "--username"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_creating_an_account_with_missing_password():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_account(
        email='random555@example.com',
        username='random555'
    )
    assert r.exit_code == 2
    assert 'Missing option "--password"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0



# Invalid Fields
def test_user_get_validation_error_when_creating_an_account_with_invalid_password():
    pass