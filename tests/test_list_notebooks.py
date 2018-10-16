from tests.constants import Image
from tests.test_utils import TestWrapper


# Workflow

def test_user_sees_the_list_of_notebooks_successfully():
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
def test_user_gets_validation_error_when_listing_notebooks_while_being_logged_out():
    TestWrapper.check_list_notebooks_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid Fields
