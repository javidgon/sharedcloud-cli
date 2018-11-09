from tests.constants import Image, Message
from tests.test_utils import TestWrapper, TestUtils


# Workflow
def test_user_creates_a_notebook_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'])

    TestWrapper.check_list_notebooks_output(
        expected_uuid=[notebook_uuid],
        expected_name=[notebook_name],
        expected_image=[Image.WEB_CRAWLING_PYTHON36['path']],
    )

    TestWrapper.delete_notebook_successfully(uuid=notebook_uuid)
    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_creating_a_notebook_while_being_logged_out():
    TestWrapper.create_notebook_unsuccessfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_creating_a_notebook_with_missing_name():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_notebook_unsuccessfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], error_code=2,
        msg='Missing option "--name"')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_notebook_with_missing_image_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_notebook_unsuccessfully(
        name=TestUtils.generate_random_seed(), error_code=2,
        msg='Missing option "--image-uuid"')

    TestWrapper.delete_account_successfully()


# Invalid Fields

def test_user_get_validation_error_when_creating_a_notebook_with_invalid_image_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_notebook_unsuccessfully(
        name=TestUtils.generate_random_seed(), image_uuid='blabla', error_code=2,
        msg='Invalid value for "--image-uuid"')

    TestWrapper.delete_account_successfully()
