# Repo in volume

This is an alternative approach to high performance with docker on OSX and windows.
It is very simple, we just:

- Mount a persistent docker volume for the repo root.
- Clone the repo within the container.
- Work in the container just like you would with a virtual machine.


# How to

Uncomment the following two lines in devcontainer.json (do NOT commit this change):
```
	// "workspaceMount": "source=devilry_dockerdev_repo,destination=/workspace,type=volume",
	// "workspaceFolder": "/workspace",
```

Then do the following (you only need to do this once unless you remove the ``devilry_dockerdev_repo`` docker volume):

1. Open the repo locally vscode and run ``Remote containers: Reopen and reopen in container``.
2. Wait for the container to finish building. Just ignore all the popups that ask you to install or select anything.
   This will solve itself when we get dependencies installed later on.
3. Open a shell. You should start in the ``/workspace/`` folder, and pipenv should have created
   ``Pipfile`` and ``Pipfile.lock``. Remove those files (just run ``rm -r *``).
4. Clone the repo into ``/workspace`` with:

   ```
   $ git clone git@github.com:devilry/devilry-django.git /workspace/
   ```

Now you have everything you need inside the docker container/volume, but some things like pipenv install
failed in step (1/2). The easiest fix is:

1. Close the vscode window.
2. Re-open the project in vscode.
3. Select the "reopen in container" popup that shows up, or run ``Remote containers: Reopen and reopen in container``.
   Just ignore all the popups that ask you to install or select anything.
   This will solve itself when we get dependencies installed.
4. You may have to _Select python interpreter_ in vscode when pipenv install is done. Select
   the interpreter in ``~/persistent/virtualenvs/...``. You will normally need to open
   a new terminal after starting up the container since the initial terminal will
   open before the python extension that selects the virtualenv is loaded.

As long as you do not remove the ``devilry_dockerdev_repo`` docker volume, you just have to do (2) and (3) each
time you open vscode to get back into the container and develop as usual.


# Why?
This is very useful for the following reasons:

- It is simple and have no external dependencies.
- It performs very well (it has close to local/native disk IO performance).
- It does not affect the local filesystem at all - it is completely isolated. You can even work efficiently in
  multiple branches by changing the name of the ``devilry_dockerdev_repo`` volume i devcontainer.json
  (E.g.: devilry_dockerdev_repo_experimentalbranch1).


# Move files to and from the host machine
We mount the HOME directory of the host filesystem at ``/host_userhome`` within
the container. You can use that to move files to and from the container. You can also
setup mutagen.io as explained below.


# Using mutagen.io to sync host and docker image
**WARNING**: Make sure you have comitted and pushed all changes both locally (on the host machine), and within the docker container BEFORE
you start syncing with mutagen. Just in case something goes wrong.

NOTE: You can use this BEFORE following the steps above that instructs you to clone the repo into your
container. When you do it in the order with mutagen sync first, you avoid having to manually
clone the repo within the container.


## Install mutagen:
```
$ brew install mutagen-io/mutagen/mutagen
```

## First time setup

Setup a docker container for sync:
```
$ docker volume create arbeiderpartiet_dockerdev_mutagensync_volume
$ docker container create --name devilry_dockerdev_mutagensync_container -v devilry_dockerdev_repo:/volumes/sync mutagenio/sidecar
$ docker container start devilry_dockerdev_mutagensync_container
$ docker exec devilry_dockerdev_mutagensync_container chown 1000:1000 /volumes/sync
$ docker exec devilry_dockerdev_mutagensync_container chmod go+w /volumes/sync
```
**NOTE:** you need to do this again if you delete the ``devilry_dockerdev_mutagensync_container`` docker container
or the ``devilry_dockerdev_repo`` docker volume.

Create/start the mutagen sync daemon (the name can be anything you want, it is just used with the other mutagen commands):
```
$ mutagen sync create --name="devilry-dockerdev-sync" --sync-mode=two-way-resolved --default-owner-beta="id:1000" --default-group-beta="id:1000" --ignore 'node_modules/,.pytest_cache/,.vscode-atest-temp/,dbdev_tempdata/' . docker://devilry_dockerdev_mutagensync_container/volumes/sync
```

Run the following command, and wait for it to say _Status: Watching for changes_:
```
$ mutagen sync monitor devilry-dockerdev-sync
```

Mutagen sync is now ready. You can just CTRL-C out of the mutagen sync monitor process. The sync will continue in the background.

## Pause and resume the mutagen sync
If you want to save some resource because you are not working on this project, simply pause
the sync process and stop the docker image with:

```
$ mutagen sync pause devilry-dockerdev-sync && docker container stop devilry_dockerdev_mutagensync_container
```

The use the following commands to resume:
```
$ docker container start devilry_dockerdev_mutagensync_container && mutagen sync resume devilry-dockerdev-sync
```

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
$ mutagen sync terminate devilry-dockerdev-sync
```


### Full mutagen cleanup
You normally do not need to do this unless something is wrong, or you need to change
the arguments for ``mutagen sync create``, but if you want a full cleanup, do this:
```
$ mutagen sync terminate devilry-dockerdev-sync
$ docker container stop devilry_dockerdev_mutagensync_container
$ docker container rm devilry_dockerdev_mutagensync_container
$ docker volume rm devilry_dockerdev_mutagensync_volume
```
After this, you can do the steps in _First time setup_ to start again
with a clean slate.
