import os

from tests.constants import Image, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_a_notebook_with_code_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'])

    TestWrapper.update_notebook_successfully(
        uuid=notebook_uuid, image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'])

    TestWrapper.check_list_notebooks_output(
        expected_uuid=[notebook_uuid],
        expected_name=[notebook_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
    )

    TestWrapper.delete_notebook_successfully(uuid=notebook_uuid)

    TestWrapper.delete_account_successfully()


def test_user_updates_a_notebook_with_file_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'])

    TestWrapper.update_notebook_successfully(
        uuid=notebook_uuid, image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'])

    TestWrapper.check_list_notebooks_output(
        expected_uuid=[notebook_uuid],
        expected_name=[notebook_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
    )

    TestWrapper.delete_notebook_successfully(uuid=notebook_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_updating_a_notebook_while_being_logged_out():
    TestWrapper.update_notebook_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_updating_a_notebook_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_notebook_unsuccessfully(
        name=TestUtils.generate_random_seed(), error_code=2,
        msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully()

# Invalid Fields

def test_user_get_validation_error_when_updating_an_unknown_notebook():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_notebook_unsuccessfully(
        uuid=TestUtils.generate_uuid(), name=TestUtils.generate_random_seed(),
        image_uuid=Image.STANDARD_NODE8['uuid'], error_code=1,
        msg=Message.NO_RESOURCE_FOUND)

    TestWrapper.delete_account_successfully()

def test_user_get_validation_error_when_updating_a_notebook_with_invalid_image_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_notebook_unsuccessfully(
        uuid=account_uuid, name=TestUtils.generate_random_seed(), image_uuid='blabla', error_code=2,
        msg='Invalid value for "--image-uuid"')

    TestWrapper.delete_account_successfully()
