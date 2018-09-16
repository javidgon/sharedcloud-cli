import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Missing fields
def test_user_get_validation_error_when_creating_an_instance_with_missing_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.start_instance()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_creating_an_instance_with_missing_seconds():
    # TODO: This can only be done after we figure out how to stop the process
    pass

# Invalid Fields
def test_user_get_validation_error_when_creating_an_instance_with_invalid_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.start_instance(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9'
    )
    # TODO: Maybe here we should also raise an exit_code 2
    assert r.exit_code == 0
    assert 'Not found Instance' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0