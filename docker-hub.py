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


def create(args):
    print(args)


def trigger(args):
    print(args)


def rebase(args):
    print(args)


def push(args):
    print(args)


def main(argv):
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('--version', action='version',
                        version=('%(prog)s version ' + version))

    parser.add_argument('--repo', action='store', default=dflt_repo,
                        help=('path to the git repo to maintain (default=%s)'
                              % dflt_repo))

    subparsers = parser.add_subparsers(help=None)

    parser_create = subparsers.add_parser('create',
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
    parser_trigger.set_defaults(func=trigger)

    parser_rebase = subparsers.add_parser('rebase', help='rebase branches')
    parser_rebase.add_argument(
        '--all', action='store_true',
        help='rebase all branches on master')
    parser_rebase.add_argument(
        '--branch', action='append',
        help='branch name (can be supplied multiple times)')
    parser_rebase.set_defaults(func=rebase)

    parser_push = subparsers.add_parser('push',
                                        help='push modified branches')
    parser_push.add_argument(
        '-n', '--dry-run', action='store_true',
        help='only display the "git push" commands to run')
    parser_push.set_defaults(func=push)

    args = parser.parse_args(argv)
    if ("func" in args):
        func = args.func
        del args.func
        func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
