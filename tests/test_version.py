from sharedcloud_cli.constants import __VERSION__
from tests.test_utils import TestUtils


# Workflow
def test_user_can_see_the_cli_version():
    r = TestUtils.show_version()
    assert r.exit_code == 0
    assert __VERSION__ in r.output
