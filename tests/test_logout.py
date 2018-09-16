from tests.test_utils import TestUtils


def test_user_logout_and_get_warning_because_he_is_already_logout():
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'You were already logged out' in r.output
