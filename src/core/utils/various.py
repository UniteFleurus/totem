import os


def env(key, default=None, boolean=False):
    if boolean and default not in (True, False):
        raise Exception("Expected boolean for `default`")

    value = os.getenv(key, str(default or ""))

    return (value.lower() == "true") if boolean else value
