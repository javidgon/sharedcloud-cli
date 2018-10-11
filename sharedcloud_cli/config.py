import click


class Config(object):
    """
    Context object that will contain the user token.
    """

    def __init__(self):
        self.token = None


pass_config = click.make_pass_decorator(Config, ensure=True)

