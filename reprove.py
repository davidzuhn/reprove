import argparse
import json
import os
import shutil
import sys

config = {'force': False}


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", help="repository manifest file", action="store")
    parser.add_argument("--builddir", help="destination for checked out repositories", action="store")
    parser.add_argument("--force", help="use destination dir, even if it exists", action="store_true")
    args = parser.parse_args()

    if args.manifest:
        config['manifest'] = args.manifest
    if args.builddir:
        config['builddir'] = args.builddir

    if 'builddir' not in config:
        print "Must specify a destination build directory (--builddir pathname)"
        sys.exit(1)

    if 'manifest' not in config:
        print "Must specify a destination build directory (--builddir pathname)"
        sys.exit(1)


def check_builddir():
    if os.path.isfile(config['builddir']):
        if config['force']:
            shutil.rmtree(config['builddir'])
        else:
            print "Unwilling to overwrite destination builddir of {0}".format(config['builddir'])
            sys.exit(1)

    os.mkdir(config['builddir'])


def read_manifest_file():
    if not os.path.isfile(config['manifest']):
        print "No file found for manifest at {0}".format(config['manifest'])

    with open(config['manifest'], "r") as manifest_file:
        config['repos'] = json.load(manifest_file)

    print json.dumps(config['repos'], sort_keys=True, indent=4)


def main():
    get_config()

    check_builddir()

    read_manifest_file()


if __name__ == "__main__":
    main()
    sys.exit(0)
