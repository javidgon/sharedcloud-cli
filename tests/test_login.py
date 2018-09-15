from click.testing import CliRunner

from tests.test_utils import TestUtils

runner = CliRunner()


def test_user_login_and_get_validation_error_with_invalid_credentials():
    result = TestUtils.login('fake_user', 'fake_password')
    assert 'Unable to log in with provided credentials' in result.output


def test_user_login_succeed_with_valid_credentials():
    # TODO: We should check that the token is actually stored
    result = TestUtils.login()
    assert 'Successfully logged in' in result.output
    TestUtils.logout()
