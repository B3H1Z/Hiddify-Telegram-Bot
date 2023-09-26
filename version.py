import argparse

# Define the version number
__version__ = "5.5.0-pre"


def version():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    version()
