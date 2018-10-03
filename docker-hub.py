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
import sys

dirpath = os.path.realpath(os.path.dirname(__file__))
prog = os.path.basename(__file__)
version = "0.1.0"

# default values
dflt_repo = os.path.normpath(dirpath + "/../docker-coq")


def create(repo, name):
    print("""
cd %s
git checkout -b %s master
echo Check_then_run: %s push -n
""" % (repo, name, prog))


def trigger(image, all, branch, token):
    print("""
curl -H "Content-Type: application/json" --data '{"source_type": "Branch", "source_name": "%s"}' -X POST https://registry.hub.docker.com/u/%s/trigger/%s/

curl -H "Content-Type: application/json" --data '{"build": true}' -X POST https://registry.hub.docker.com/u/%s/trigger/%s/
""" % (branch, image, token, image, token))


def rebase(repo, all, branch):
    print("""
for each specified branch b (or for all branches):
    cd %s
    git rebase master b
""" % repo)


def push(repo, dry_run):
    print("""
cd %s
git fetch origin
# prepend echo if dry_run
for all recent branches b:
    git push origin b
    sleep 2s
""" % repo)


def main(argv):
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--repo', action='store', default=dflt_repo,
                               help=('path to the source git repo (default=%s)'
                                     % dflt_repo))

    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('--version', action='version',
                        version=('%(prog)s version ' + version))

    subparsers = parser.add_subparsers(help=None)

    parser_create = subparsers.add_parser('create',
                                          parents=[parent_parser],
                                          help='create a new stable branch')
    parser_create.add_argument('name', action='store',
                               help='branch name (stable version)')
    parser_create.set_defaults(func=create)

    parser_trigger = subparsers.add_parser('trigger',
                                           help='trigger rebuild of branches')
    parser_trigger.add_argument(
        '--all', action='store_true',
        help='trigger rebuild of all branches')
    parser_trigger.add_argument(
        '--branch', action='append',
        help='branch name (can be supplied multiple times)')
    parser_trigger.add_argument('image', action='store',
                                help='user/repo on Docker Hub')
    parser_trigger.add_argument('token', action='store',
                                help='Docker Hub token')
    parser_trigger.set_defaults(func=trigger)

    parser_rebase = subparsers.add_parser('rebase',
                                          parents=[parent_parser],
                                          help='rebase branches')
    parser_rebase.add_argument(
        '--all', action='store_true',
        help='rebase all branches on master')
    parser_rebase.add_argument(
        '--branch', action='append',
        help='branch name (can be supplied multiple times)')
    parser_rebase.set_defaults(func=rebase)

    parser_push = subparsers.add_parser('push',
                                        parents=[parent_parser],
                                        help='push modified branches')
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

# ./docker-hub.py -h
# ./docker-hub.py create -h
# ./docker-hub.py trigger -h
# ./docker-hub.py rebase -h
# ./docker-hub.py push -h
