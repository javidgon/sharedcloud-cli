import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Logged out
def test_user_get_validation_error_when_listing_functions_while_being_logged_out():
    r = TestUtils.list_functions()

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields


# Invalid Fields