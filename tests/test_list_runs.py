from tests.test_utils import TestUtils

# Logged out
def test_user_get_validation_error_when_listing_runs_while_being_logged_out():
    r = TestUtils.list_runs()

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields


# Invalid Fields