# docker-hub-helper

## Summary

This repo gathers a python3 program [dhh](./dhh),
to help maintain multi-branches, automated-build repos on Docker Hub.

## Installation

* Either put the `dhh` program in the `PATH`;
* Or add an alias to your `~/.bashrc`, e.g.: `alias dhh='/full/path/to/dhh'`

## Usage summary

```
usage: dhh [-h] [--version]
           {branches,reset,create,trigger,rebase,push,delete} ...

A tool to help maintain multi-branches, automated-build repos on Docker Hub.
Assume the considered Git repo has master as main branch, origin as remote.

positional arguments:
  {branches,reset,create,trigger,rebase,push,delete}
    branches            fetch, checkout and list remote branches
    reset               reset specified branches w.r.t. origin
    create              fetch and create a stable branch from [origin/]master
    trigger             trigger rebuild of branches
    rebase              fetch and rebase branches on master
    push                push modified branches to trigger rebuild
    delete              delete a local and remote branch

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

The location of the local Git repo can be specified by an argument
`--repo …/path/to/git/repo`, which is accepted by all sub-commands,
except `trigger`. If the option is omitted, it defaults to `--repo=.`.

## Use cases

### Goal: help maintain a multi-branches Git repo for Docker Hub

The considered repo should contain:

* a remote `origin`;
* a branch `master` that triggers no automated build but is intended
  to gather changes that are common to all images;
* several branches that triggers an automated build for the
  corresponding Docker image; these branches typically have a uniform
  naming convention (which is albeit not enforced by `dhh`) and are
  intended to be rebased on `master` then forced-pushed to incorporate
  changes performed in `master`.

### Update if the remote repo was forced-pushed by another maintainer or so

If there are several local clones of this Git repository (e.g. used by
different maintainers), the following commands allow one to update the
considered clone:

```bash
cd $repo

# fetch the repo, checkout remote branches, and display differences
# between remote and local branches thanks to "git branch -vv":
dhh branches

# if need be, one can then reset the local branches with respect to
# the remote ones:
dhh reset --all

# for more information on the option -b:
dhh reset --help
```

### Add a commit in `master` and rebase all stable branches

```bash
cd $repo
git checkout master
git commit -a -m "Do something"

# fetch the repo, and rebase all branches on master (i.e. forall local
# branch br, replace br with (the newest branch among br and origin/br)
# rebased on master)
dhh rebase --all

# for more information on the option -b:
dhh rebase --help

# dry-run before pushing
dhh push -n

# push local changes to trigger the builds
dhh push
```

### Dockerize a new beta release of Coq

E.g., Coq version `8.9+beta1`:

```bash
cd …/docker-coq

# fetch the repo
dhh branches

# note that the last argument is the name of the branch and Docker tag
# that cannot contain the character "+":
dhh create --from beta -e COQ_VERSION=8.9+beta1 8.9-beta1

# TODO: Open Docker Hub's build settings
# TODO: Add an automated build rule for "8.9-beta1"

# dry-run before pushing
dhh push -n

# push local changes to trigger the build
dhh push
```

### Dockerize a new stable release of Coq

E.g., Coq version `8.9.0`:

(the main differences w.r.t. the previous section are the absence of
`--from beta`, and the deletion of the beta branch and image)

```bash
cd …/docker-coq

# fetch the repo
dhh branches

dhh create -e COQ_VERSION=8.9.0 8.9.0

# TODO: Open Docker Hub's build settings
# TODO: Replace "8.9-beta1" with "8.9.0"

# delete the local and remote branch for the beta
dhh delete 8.9-beta1

# dry-run before pushing
dhh push -n

# push local changes to trigger the build
dhh push
```

### Dockerize a new point release of Coq

E.g., Coq patchlevel `8.9.1`:

```bash
cd …/docker-coq

# fetch the repo
dhh branches

dhh create --from 8.9.0 -e COQ_VERSION=8.9.1 8.9.1

# TODO: Open Docker Hub's build settings
# TOOD: Replace "8.9.0" with "8.9.1"

# delete the local and remote branch for the old patchlevel
dhh delete 8.9.0

# dry-run before pushing
dhh push -n

# push local changes to trigger the build
dhh push
```

### Dockerize a new stable release of math-comp

E.g., math-comp `1.9.0` for Coq `8.7`, `8.8`, `8.9`, `8.10`, `dev`:

```bash
cd …/docker-mathcomp

# fetch the repo
dhh branches

MC=1.9.0; for COQ in 8.7 8.8 8.9 8.10 dev; do \
  dhh create -f coqorg/coq:$COQ -e MATHCOMP_VERSION=$MC $MC-coq-$COQ; \
  echo "TODO: Add a Docker Hub automated build rule for $MC-coq-$COQ"; \
done

# dry-run before pushing
dhh push -n

# push local changes to trigger the builds
dhh push
```

## Author and License

This tool was written by [Érik Martin-Dorel](https://github.com/erikmd).
It is distributed under the
[BSD-3 license](https://opensource.org/licenses/BSD-3-Clause).
