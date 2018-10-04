# docker-scripts

## Summary

This repo gathers a python3 program [docker-hub.py](./docker-hub.py),
to help maintain multi-branches, automated-build repos on Docker Hub.

## Installation

Put this program in the `PATH` and run: `docker-hub.py -h`

## Example

To dockerize a new stable branch of Coq, e.g. the patchlevel `8.8.2`:

```bash
docker-hub.py branches
docker-hub.py create --coq --from=8.8.1 8.8.2
  # open Docker Hub's build settings
  # and replace "8.8.1" with "8.8.2"; then
docker-hub.py delete 8.8.1
docker-hub.py push -n
docker-hub.py push
```

Other commands are available (`docker-hub.py trigger`, `docker-hub.py rebase`)

## Author and License

This tool was written by [Érik Martin-Dorel](https://github.com/erikmd).
It is distributed under the
[BSD-3 license](https://opensource.org/licenses/BSD-3-Clause).
