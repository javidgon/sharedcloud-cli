import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Missing fields
def test_user_get_validation_error_when_updating_a_function_with_missing_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_function(
        runtime='python36'
    )
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


# Invalid Fields

def test_user_get_validation_error_when_updating_a_function_with_invalid_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name='example1',
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Not found resource with UUID' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_updating_a_function_with_invalid_code():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name='example1',
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Not found resource' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_updating_a_function_with_invalid_runtime():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name='example1',
        runtime='python99',
        code='def handler(event): print(2)'
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--runtime":' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

