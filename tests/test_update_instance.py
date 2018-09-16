import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Missing fields
def test_user_get_validation_error_when_updating_an_instance_with_missing_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_instance()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


# Invalid Fields
def test_user_get_validation_error_when_updating_an_instance_with_invalid_uuid():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_instance(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
   )
    assert r.exit_code == 2
    assert 'Not found resource' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


def test_user_get_validation_error_when_updating_an_instance_with_invalid_price_per_hour():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.update_instance(
        name='example1',
        price_per_hour='blabla',
        max_num_jobs=5
    )
    # TODO: Maybe here we should also raise an exit_code 2
    assert r.exit_code == 2
    assert 'Invalid value for "--price_per_hour"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_updating_an_instance_with_invalid_max_num_jobs():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        name='example1',
        price_per_hour=1.5,
        max_num_jobs='blabla'
    )
    print(r.exit_code, r.output)
    assert r.exit_code == 2
    assert 'Invalid value for "--max_num_jobs"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


