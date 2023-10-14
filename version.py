import argparse

# Define the version number
__version__ = "5.8.0"


def version():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()
    return args

def is_version_less(version1, version2):
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))

    for part1, part2 in zip(v1_parts, v2_parts):
        if part1 < part2:
            return True
        elif part1 > part2:
            return False

    # If both versions are identical up to the available parts
    return False

if __name__ == "__main__":
    version()
