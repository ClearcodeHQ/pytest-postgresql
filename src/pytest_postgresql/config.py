from pytest import FixtureRequest


def get_config(request: FixtureRequest) -> dict:
    """Return a dictionary with config options."""
    config = {}
    options = [
        "exec",
        "host",
        "port",
        "user",
        "password",
        "options",
        "startparams",
        "logsprefix",
        "unixsocketdir",
        "dbname",
        "load",
        "postgres_options",
    ]
    for option in options:
        option_name = "postgresql_" + option
        conf = request.config.getoption(option_name) or request.config.getini(option_name)
        config[option] = conf
    return config
