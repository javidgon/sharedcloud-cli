import os

import click

from sharedcloud_cli.cli.account import account
from sharedcloud_cli.cli.function import function
from sharedcloud_cli.cli.gpu import gpu
from sharedcloud_cli.cli.image import image
from sharedcloud_cli.cli.instance import instance
from sharedcloud_cli.cli.job import job
from sharedcloud_cli.cli.login import login
from sharedcloud_cli.cli.logout import logout
from sharedcloud_cli.cli.offer import offer
from sharedcloud_cli.cli.run import run
from sharedcloud_cli.cli.version import version
from sharedcloud_cli.config import pass_config
from sharedcloud_cli.constants import DATA_FOLDER
from sharedcloud_cli.utils import _read_user_token, _get_cli_version


@click.group()
@pass_config
def cli(config):
    """
    Sharedcloud CLI tool to:

    Check the help available for each command listed below.
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    config.token = _read_user_token()
    config.version = _get_cli_version()


cli.add_command(version)
cli.add_command(account)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(function)
cli.add_command(run)
cli.add_command(job)
cli.add_command(image)
cli.add_command(offer)
cli.add_command(gpu)
cli.add_command(instance)
