# see http://stackoverflow.com/questions/1783405/checkout-remote-git-branch
# and http://stackoverflow.com/questions/791959/download-a-specific-tag-with-git

# check out a set of repositories to match the manifest file


import argparse
import json
import os
import shutil
import subprocess
import sys

CONFIG = {
    'force': False,
    'manifest': None,
    'builddir': None
}


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", help="repository manifest file", action="store")
    parser.add_argument("--builddir", help="destination for checked out repositories", action="store")
    parser.add_argument("--force", help="use destination dir, even if it exists", action="store_true")
    args = parser.parse_args()

    if args.manifest:
        CONFIG['manifest'] = args.manifest
    if args.builddir:
        CONFIG['builddir'] = args.builddir
    if args.force:
        CONFIG['force'] = True

    if 'builddir' not in CONFIG:
        print "Must specify a destination build directory (--builddir pathname)"
        sys.exit(1)
    else:
        check_builddir()

    if 'manifest' not in CONFIG:
        print "Must specify a destination build directory (--builddir pathname)"
        sys.exit(1)
    else:
        read_manifest_file()


def check_builddir():
    if os.path.exists(CONFIG['builddir']):
        if CONFIG['force']:
            shutil.rmtree(CONFIG['builddir'])
            print "Removing existing data at {0}".format(CONFIG['builddir'])
        else:
            print "Unwilling to overwrite destination builddir of {0}".format(CONFIG['builddir'])
            sys.exit(1)

    os.mkdir(CONFIG['builddir'])


def read_manifest_file():
    if not os.path.isfile(CONFIG['manifest']):
        print "No file found for manifest at {0}".format(CONFIG['manifest'])

    with open(CONFIG['manifest'], "r") as manifest_file:
        CONFIG['repos'] = json.load(manifest_file)

        # print json.dumps(config['repos'], sort_keys=True, indent=4)


def validate_repo_entry(repo):
    if repo is None:
        return False

    if 'repository' not in repo:
        print "Manifest repository entry without repository tag:\n{0}".format(json.dumps(repo, indent=True))
        return False

    return True


def run_git(args, directory=None):
    original_directory = None
    if directory is not None:
        original_directory = os.getcwd()
        os.chdir(directory)

    args.insert(0, "/usr/bin/git")
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT, shell=False)
    except subprocess.CalledProcessError as e:
        print "Returned error code from {1}: {0}".format(e.returncode, e.cmd)
        output = e.output

    if original_directory is not None:
        os.chdir(original_directory)

    print output

    return output


def strip_end(text, suffix):
    if suffix is None:
        return text

    if not text.endswith(suffix):
        return text
    return text[:len(text) - len(suffix)]


def checkout_repo(repo):
    repo_url = repo['repository']
    print "Checkout repo {0}".format(repo_url)

    basename = strip_end(os.path.basename(repo_url), ".git")

    print "BASENAME {0}".format(basename)

    command = ["clone", repo_url]
    if 'checked-out-directory-name' in repo:
        basename = repo['checked-out-directory-name']
        command.append(basename)

    run_git(command, CONFIG['builddir'])

    working_directory = os.path.join(CONFIG['builddir'], basename)


    # check in this order...

    # a commit id is VERY specific
    # a tag is almost as specific
    # a branch name is slightly less specific

    reset_id = None
    if 'commit_id' in repo:
        reset_id = repo['commit_id']
    elif 'tag' in repo:
        reset_id = repo['tag']

    if reset_id is not None:
        run_git(["reset", "--hard", reset_id], working_directory)
        return

    if 'branch' in repo:
        run_git(["fetch", "-a"], working_directory)
        run_git(["checkout", repo['branch']], working_directory)


def get_repositories():
    repo_list = CONFIG['repos']['repositories']
    if repo_list is None:
        print "No repository list found in manifest file"
        sys.exit(2)
    else:
        for repo in repo_list:
            if validate_repo_entry(repo):
                checkout_repo(repo)


def main():
    get_config()

    if 'repos' in CONFIG:
        get_repositories()
    else:
        print "NO repository info found in manifest: {0}".format(CONFIG['manifest'])


if __name__ == "__main__":
    main()
    sys.exit(0)
