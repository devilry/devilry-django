# Devcontainer (docker+vscode) setup for devilry

# Setup mutagen

## Mutagen IO info
Mutagen IO is a good approach to high performance with docker on OSX and windows.
It is very simple, we just:

- Mount a persistent docker volume for the repo root.
- Clone the repo within the container via mutagen.io.
- Work in the container just like you would with a virtual machine.

We use mutagen by default in ``devilry``.

## Using mutagen.io to sync host and docker image
**WARNING**: Make sure you have comitted and pushed all changes both locally (on the host machine), and within the docker container BEFORE
you start syncing with mutagen. Just in case something goes wrong. First time you read this (before you setup mutagen), just make sure it
is comitted and pushed locally.


### Install mutagen:
On OSX with homebrew:
```
$ brew install mutagen-io/mutagen/mutagen
```

### First time mutagen setup

Setup a docker container for sync:
```
$ tools/devcontainer-helpers/bin/devilry_mutagen_init.sh
```

Run the following command, and wait for it to say _Status: Watching for changes_:
```
$ tools/devcontainer-helpers/bin/devilry_mutagen_monitor.sh
```

Mutagen sync is now ready. You can just CTRL-C out of the mutagen sync monitor process. The sync will continue in the background.

Reopen and reload container by using `Remote-containers`

### Pause and resume the mutagen sync
If you want to save some resource because you are not working on this project, simply pause
the sync process and stop the docker image with:

```
$ tools/devcontainer-helpers/bin/devilry_mutagen_pause.sh
```

The use the following commands to resume:
```
$ tools/devcontainer-helpers/bin/devilry_mutagen_start.sh
```


# Develop with the docker setup (after setting up mutagen)

## VSCode: Develop with docker via VSCode
If you just have the ``Remote - Containers`` extension (made by the vscode team), you should be asked if you want to open the project in the remote container when you open the project. If you are not asked, you
can use the ``Remote - Containers`` at the bottom left of the vscode window,
or one of the following commands in the command palette:

- ``Remote-Container: Open folder in Container``
- ``Remote-Container: Rebuild and Reopen in Container``
- ``Remote-Container: Reopen in Container``

Since we have a ready-to-use configuration in ``.devcontainer/``, this should *just work*. Check out https://code.visualstudio.com/docs/remote/containers-tutorial for more details.

### VSCode: Python interpreter not found
You will get this if you have a python file open before ``poetry install`` is done. Just wait for ``poetry install`` to finish running (part of starting up the container),
and run ``Develop: Reload Window`` command palette action.


### VSCode: Run CLI commands
Just start up a terminal via VSCode. This starts a terminal in the docker container. Run CLI commands just like you would on your local machine.


### VSCode: Rebuild the docker image
Run the ``Remote-Container: Rebuild and Reopen in Container`` command palette command.



# More mutagen tips and tricks

## Things to be careful about with mutagen sync

1. **We do sync .git/.** It does not really matter if you commit on host or in the container, but you should only do one of,
   and within the container is recommended since that is what the git integration in vscode does when you have the repo open
   in the container.
   Comitting and doing git operations like stage on both ends can lead to corruption of ``.git/``.
2. Starting the sync with uncomitted changes should be safe, but it is recommended to have a clean git with all changes up to
   date on both host and container before starting the sync.


## Useful mutagen commands

### Show sync progress and events in realtime
```
$ mutagen sync monitor devilry-dockerdev-sync
```

### Show/browse files that has been synced
Just use docker exec with normal linux commands as you would with any
docker image. Useful for debugging/checking that the sync works as expected..
```
$ docker exec devilry_dockerdev_mutagensync_container ls -l /volumes/sync/
$ docker exec devilry_dockerdev_mutagensync_container cat /volumes/sync/Pipfile
... etc ..
```

### List sync sessions
```
$ mutagen sync list
```

### Terminate the sync session
```
$ tools/devcontainer-helpers/bin/devilry_mutagen_stop.sh
```


### Full mutagen cleanup
You normally do not need to do this unless something is wrong, or you need to change
the arguments for ``mutagen sync create``, but if you want a full cleanup, do this:
```
$ tools/devcontainer-helpers/bin/devilry_mutagen_delete.sh
```
After this, you can do the steps in _First time setup_ to start again
with a clean slate.
