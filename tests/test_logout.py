from click.testing import CliRunner

from tests.test_utils import TestUtils

runner = CliRunner()


def test_user_logout_and_get_warning_because_he_is_already_logout():
    result = TestUtils.logout()
    assert 'You were already logged out' in result.output

def test_user_logout_succeed_when_he_is_logged_in():
    # TODO: We should check that the token is actually deleted
    # We login first to make sure that we can logout afterwards
    result = TestUtils.login()

    result = TestUtils.logout()
    assert 'Successfully logged out' in result.output
