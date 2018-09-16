import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Missing fields
def test_user_get_validation_error_when_creating_a_run_with_missing_function_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_run(
        parameters='((1,),(2,))'
    )
    assert r.exit_code == 2
    assert 'Missing option "--function_uuid"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


def test_user_get_validation_error_when_creating_a_run_with_missing_parameters():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_run(
        function_uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
    )
    assert r.exit_code == 2
    assert 'Missing option "--parameters"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


# Invalid Fields
def test_user_get_validation_error_when_creating_a_run_with_invalid_function_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_run(
        function_uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        parameters='((1,),(2,))'
    )
    assert r.exit_code == 2
    assert 'object does not exist.' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_creating_a_run_with_invalid_parameters():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_run(
        function_uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        parameters='((1,))'
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--parameters":' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

