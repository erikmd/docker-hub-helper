# docker-hub-helper

## Summary

This repo gathers a python3 program [dhh](./dhh),
to help maintain multi-branches, automated-build repos on Docker Hub.

## Installation

Put this program in the `PATH` and run: `dhh -h`

## Usage summary

```bash
usage: dhh [-h] [--version] {branches,create,trigger,rebase,push,delete} ...

A tool to help maintain multi-branches, automated-build repos on Docker Hub. Assume the
considered Git repo has master as main branch, origin as remote.

positional arguments:
  {branches,create,trigger,rebase,push,delete}
    branches            fetch, checkout and list remote branches
    create              fetch and create a stable branch from [origin/]master
    trigger             trigger rebuild of branches
    rebase              fetch and rebase branches on master
    push                push modified branches to trigger rebuild
    delete              delete a local and remote branch

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## Example

To dockerize a new stable branch of Coq, e.g. the patchlevel `8.8.2`:

```bash
dhh branches
dhh create --coq --from=8.8.1 8.8.2
  # open Docker Hub's build settings
  # and replace "8.8.1" with "8.8.2"; then
dhh delete 8.8.1
dhh push -n
dhh push
```

Other commands are available (`dhh trigger`, `dhh rebase`)

## Author and License

This tool was written by [Érik Martin-Dorel](https://github.com/erikmd).
It is distributed under the
[BSD-3 license](https://opensource.org/licenses/BSD-3-Clause).
