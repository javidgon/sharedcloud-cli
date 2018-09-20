from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_creating_a_run_while_being_logged_out():
    r = TestUtils.create_run(
        parameters='((1,),(2,))'
    )

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_a_run_with_missing_function_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_run(
        parameters='((1,),(2,))'
    )
    assert r.exit_code == 2
    assert 'Missing option "--function_uuid"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_run_with_missing_parameters():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_run(
        function_uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
    )
    assert r.exit_code == 2
    assert 'Missing option "--parameters"' in r.output

    _accountTearDown(account_uuid)
