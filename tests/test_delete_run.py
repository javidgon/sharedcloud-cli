from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_deleting_a_run_while_being_logged_out():
    r = TestUtils.delete_run()

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_deleting_a_run_with_missing_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.delete_run()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields
def test_user_get_validation_error_when_deleting_a_run_with_invalid_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.delete_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9')
    # TODO: Maybe here we should also raise an exit_code 2
    assert r.exit_code == 1
    assert 'Not found resource with UUID' in r.output

    _accountTearDown(account_uuid)
