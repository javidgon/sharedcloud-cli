import os

from tests.test_utils import TestUtils


username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


# Logged out
def test_user_get_validation_error_when_creating_an_instance_while_being_logged_out():
    r = TestUtils.create_instance(
        price_per_hour=1.5,
        max_num_parallel_jobs=5
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_an_instance_with_missing_name():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        price_per_hour=1.5,
        max_num_parallel_jobs=5
    )
    assert r.exit_code == 2
    assert 'Missing option "--name"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


def test_user_get_validation_error_when_creating_an_instance_with_missing_price_per_hour():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        name='example1',
        max_num_parallel_jobs=5
    )
    assert r.exit_code == 2
    assert 'Missing option "--price_per_hour"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


def test_user_get_validation_error_when_creating_an_instance_with_missing_max_num_parallel_jobs():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        name='example1',
        price_per_hour=1.5
    )
    print(r.output)
    assert r.exit_code == 2
    assert 'Missing option "--max_num_parallel_jobs"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0


# Invalid Fields
def test_user_get_validation_error_when_creating_an_instance_with_invalid_price_per_hour():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        name='example1',
        price_per_hour='blabla',
        max_num_parallel_jobs=5
    )
    # TODO: Maybe here we should also raise an exit_code 2
    assert r.exit_code == 2
    assert 'Invalid value for "--price_per_hour"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

def test_user_get_validation_error_when_creating_an_instance_with_invalid_max_num_parallel_jobs():
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.create_instance(
        name='example1',
        price_per_hour=1.5,
        max_num_parallel_jobs='blabla'
    )
    print(r.exit_code, r.output)
    assert r.exit_code == 2
    assert 'Invalid value for "--max_num_parallel_jobs"' in r.output

    r = TestUtils.logout()
    assert r.exit_code == 0

