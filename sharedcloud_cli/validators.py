import click


def _validate_at_least_one_but_only_one(ctx, main_field_value, main_field_key, other_field_key):
    """
    Validate that either "main_field" or "other_field" are passed into the CMD.

    It also validates that only one is provided.

    :param ctx: cmd context
    :param main_field_value: argument containing the main field value to compare with
    :param main_field_key: argument containing the main field name
    :param other_field_key: argument containing the other field name
    """
    if not main_field_value and other_field_key not in ctx.params:
        raise click.BadParameter('Either "{}" or "{}" parameters need to be provided'.format(
            main_field_key, other_field_key))
    if main_field_value and other_field_key in ctx.params:
        raise click.BadParameter('Only one of "{}" and "{}" parameters need to be provided'.format(
            main_field_key, other_field_key))

    return main_field_value


def _validate_code(ctx, param, code):
    return _validate_at_least_one_but_only_one(ctx, code, 'code', 'file')


def _validate_file(ctx, param, file):
    return _validate_at_least_one_but_only_one(ctx, file, 'file', 'code')
