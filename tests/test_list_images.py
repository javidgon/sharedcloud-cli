from tests.constants import Image, InstanceType
from tests.test_utils import TestWrapper


# Workflow
def test_user_sees_the_list_of_images_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_list_images_output(
        expected_registry_path=[
            Image.STANDARD_NODE8['path'],
            Image.TENSORFLOW_PYTHON27['path'],
            Image.WEB_CRAWLING_PYTHON27['path'],
            Image.TENSORFLOW_PYTHON36['path'],
            Image.WEB_CRAWLING_PYTHON36['path'],
        ],
        expected_description=[
            Image.STANDARD_NODE8['description'],
            Image.TENSORFLOW_PYTHON27['description'],
            Image.WEB_CRAWLING_PYTHON27['description'],
            Image.TENSORFLOW_PYTHON36['description'],
            Image.WEB_CRAWLING_PYTHON36['description'],
        ],
        expected_num_images=5
    )

    TestWrapper.delete_account_successfully()


def test_user_wants_to_see_only_the_downloaded_images():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=1
    )

    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.check_list_images_output(
        only_downloaded=True,
        expected_registry_path=[
            Image.WEB_CRAWLING_PYTHON36['path']
        ],
        expected_description=[
            Image.WEB_CRAWLING_PYTHON36['description'],
        ],
        expected_num_images=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)
    TestWrapper.delete_account_successfully()


def test_user_wants_to_see_only_the_downloaded_images_but_he_doesnt_have_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)
    try:
        TestWrapper.check_list_images_output(
            only_downloaded=True,
            expected_registry_path=[],
            expected_description=[],
            expected_num_images=0
        )
    except AssertionError:
        TestWrapper.delete_account_successfully()
    else:
        raise AssertionError


# Logged out

def test_user_gets_validation_error_when_listing_images_while_being_logged_out():
    TestWrapper.check_list_images_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid fields
