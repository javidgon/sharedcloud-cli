import os

from tests.test_utils import TestUtils

username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Missing fields
def test_user_get_validation_error_when_login_with_missing_username():
    r = TestUtils.login(password=password)
    assert r.exit_code == 2
    assert 'Missing option "--username"' in r.output


def test_user_get_validation_error_when_login_with_missing_password():
    r = TestUtils.login(username=username)
    assert r.exit_code == 2
    assert 'Missing option "--password"' in r.output


# Invalid fields
def test_user_login_and_get_validation_error_with_invalid_credentials():
    r = TestUtils.login('fake_user', 'fake_password')
    assert r.exit_code == 1
    assert 'Unable to log in with provided credentials' in r.output