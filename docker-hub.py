#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018  Érik Martin-Dorel
#
# Helper script to maintain multi-branches, automated-build repos on Docker Hub
#
# Licensed under BSD-3 <https://opensource.org/licenses/BSD-3-Clause>
#
# Report bugs to erik@martin-dorel.org

import argparse
import os
from subprocess import call, check_call, check_output, DEVNULL
import sys
import time

dirpath = os.path.dirname(os.path.realpath(__file__))
prog = os.path.basename(__file__)
version = "0.1.0"
desc = """A tool to help maintain multi-branches, automated-build repos on Docker Hub.
Assume the considered Git repo has master as main branch, origin as remote."""

# default values
dflt_repo = os.path.normpath(dirpath + "/../docker-coq")


def coq_sed(repo, b):
    """Coq-specific code"""
    wd = os.path.expanduser(repo)
    check_call(['sed', '-i~', '-e', 's/\\(COQ_VERSION\\)=".*"/\\1="%s"/' % b,
                'Dockerfile'], cwd=wd)
    call(["git", "commit", "-a", "-m", "Dockerfile for Coq %s" % b, "-e"],
         cwd=wd)


def error(msg):
    print(msg, file=sys.stderr)
    exit(1)


def uniqify(s):
    return list(set(s))


def setminus(s1, s2):
    return list(filter(lambda e: e not in s2, s1))


def fetch(repo):
    check_call(["git", "fetch", "origin"],
               cwd=os.path.expanduser(repo))


def all_remote_branches(repo):
    """Return the list of remote branches (without origin/ prefix).

    Assume the command 'fetch(repo)' has been run."""
    byt = check_output(["git", "for-each-ref",
                        "--format", "%(refname:strip=3)",
                        "refs/remotes/origin/"],
                       cwd=os.path.expanduser(repo))
    return byt.decode('UTF-8').rstrip().split('\n')


def all_local_branches(repo):
    byt = check_output(["git", "for-each-ref",
                        "--format", "%(refname:strip=2)",
                        "refs/heads/"],
                       cwd=os.path.expanduser(repo))
    return byt.decode('UTF-8').rstrip().split('\n')


def local_newer(repo, b, remote_b=''):
    if not remote_b:
        remote_b = b + '@{u}'
    wd = os.path.expanduser(repo)
    ret = call(["git", "log", "--format=", "--exit-code",
                "%s..%s" % (remote_b, b)], cwd=wd,
               stdout=DEVNULL, stderr=DEVNULL)
    # return 1 if branch b is newer than remote_b
    # 128 if remote_b doesn't exist
    return ret != 0


def remote_newer(repo, b, remote_b=''):
    if not remote_b:
        remote_b = b + '@{u}'
    wd = os.path.expanduser(repo)
    ret = call(["git", "log", "--format=", "--exit-code",
                "%s..%s" % (b, remote_b)], cwd=wd,
               stdout=DEVNULL, stderr=DEVNULL)
    # return 1 if remote_b is newer than remote_b
    # 128 if remote_b doesn't exist
    return ret == 1


def branches(repo):
    fetch(repo)
    avoid_branches = ['HEAD']
    brs = all_local_branches(repo) + all_remote_branches(repo)
    brs = setminus(uniqify(brs), avoid_branches)
    brs.sort()
    print("Branches locally or remotely available:", brs,
          file=sys.stderr, flush=True)
    check_call(["git", "branch", "-vv"], cwd=os.path.expanduser(repo))


def create(repo, name):
    fetch(repo)
    wd = os.path.expanduser(repo)
    if remote_newer(repo, 'master', 'origin/master'):
        check_call(["git", "checkout", "-q", "master"], cwd=wd)
        check_call(["git", "pull", "--ff-only", "origin", "master"], cwd=wd)
    check_call(["git", "checkout", "-b", name, "master"], cwd=wd)
    coq_sed(repo, name)
    print("""
Ensure '%s' has been added as source branch in Docker Hub settings.

Please 'cd %s' then inspect branch '%s'
and do 'git commit -a --amend' if need be
before running '%s push -n'.""" % (name, repo, name, prog))


def trigger(image, all, branch, token):
    if not image:
        error('Error: missing image argument.')
    if not token:
        error('Error: missing token argument.')
    if image.find('/') < 0:
        error('Error: image should contain a slash "/"')

    if all:
        check_call(["curl", "-H", "Content-Type: application/json",
                    "--data",
                    '{"build": true}',
                    "-X", "POST",
                    "https://registry.hub.docker.com/u/%s/trigger/%s/"
                    % (image, token)])
        print()
    else:
        for b in branch:
            check_call(["curl", "-H", "Content-Type: application/json",
                        "--data",
                        '{"source_type": "Branch", "source_name": "%s"}' % b,
                        "-X", "POST",
                        "https://registry.hub.docker.com/u/%s/trigger/%s/"
                        % (image, token)])
            print()


def rebase(repo, all, branch):
    if not (all or branch):
        error('Error: no branch specified.')
    fetch(repo)
    avoid_branches = ['HEAD', 'master']
    if all:
        brs = all_local_branches(repo) + all_remote_branches(repo)
        # will run uniqify( ) below
    else:
        brs = branch
    brs = setminus(uniqify(brs), avoid_branches)
    brs.sort()
    print("Branches to rebase:", brs, file=sys.stderr, flush=True)
    wd = os.path.expanduser(repo)
    for b in brs:
        remote_b = 'origin/' + b
        needs_pull = remote_newer(repo, b, remote_b)
        newer = remote_b if needs_pull else b
        print("\n* Rebasing %s on master..." % newer,
              file=sys.stderr, flush=True)
        check_call(["git", "checkout", "-q", b], cwd=wd)
        if needs_pull:
            check_call(["git", "pull", "--ff-only", "origin", b], cwd=wd)
        check_call(["git", "rebase", "master"], cwd=wd)


def push(repo, dry_run):
    avoid_branches = ['HEAD']
    brs = setminus(all_local_branches(repo), avoid_branches)
    print("Local branches:", brs, file=sys.stderr, flush=True)
    wd = os.path.expanduser(repo)
    todo = []
    for b in brs:
        if local_newer(repo, b, 'origin/' + b):
            todo.append(b)
    for b in todo:
        if dry_run:
            print("git push --force-with-lease -u origin %s:%s" % (b, b))
        else:
            print("\n* Force-pushing %s to origin..." % b,
                  file=sys.stderr, flush=True)
            check_call(["git", "push", "--force-with-lease", "-u", "origin",
                        "%s:%s" % (b, b)], cwd=wd)
            time.sleep(2)


def main(argv):
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--repo', action='store', default=dflt_repo,
                               help=('path to the source git repo (default=%s)'
                                     % dflt_repo))

    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('--version', action='version',
                        version=('%(prog)s version ' + version))

    subparsers = parser.add_subparsers(help=None)

    help_br = 'fetch and list available branches'
    parser_br = subparsers.add_parser('branches',
                                      parents=[parent_parser],
                                      help=help_br, description=help_br)
    parser_br.set_defaults(func=branches)

    help_create = 'fetch and create a stable branch from [origin/]master'
    parser_create = subparsers.add_parser('create',
                                          parents=[parent_parser],
                                          help=help_create,
                                          description=help_create)
    parser_create.add_argument('name', action='store',
                               help='branch name (stable version)')
    parser_create.set_defaults(func=create)

    help_trigger = 'trigger rebuild of branches'
    parser_trigger = subparsers.add_parser('trigger',
                                           help=help_trigger,
                                           description=help_trigger)
    parser_trigger.add_argument(
        '--all', action='store_true',
        help='trigger rebuild of all branches')
    parser_trigger.add_argument(
        '-b', '--branch', action='append',
        help='branch name (can be supplied multiple times)')
    parser_trigger.add_argument('image', action='store',
                                help='user/repo on Docker Hub')
    parser_trigger.add_argument('token', action='store',
                                help='Docker Hub token')
    parser_trigger.set_defaults(func=trigger)

    help_rebase = 'fetch and rebase branches on [origin/]master'
    parser_rebase = subparsers.add_parser('rebase',
                                          parents=[parent_parser],
                                          help=help_rebase,
                                          description=help_rebase)
    parser_rebase.add_argument(
        '--all', action='store_true',
        help='rebase all branches on [origin/]master')
    parser_rebase.add_argument(
        '-b', '--branch', action='append',
        help='branch name (can be supplied multiple times)')
    parser_rebase.set_defaults(func=rebase)

    help_push = 'push modified branches to trigger rebuild'
    parser_push = subparsers.add_parser('push',
                                        parents=[parent_parser],
                                        help=help_push, description=help_push)
    parser_push.add_argument(
        '-n', '--dry-run', action='store_true',
        help='only display the "git push" commands to run')
    parser_push.set_defaults(func=push)

    args = vars(parser.parse_args(argv))
    if ("func" in args):
        func = args.pop("func")
        func(**args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])

# docker-hub.py -h
# for c in branches create trigger rebase push; do docker-hub.py $c -h; done
