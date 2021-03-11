# Develop with docker

First you need to install docker. The easiest method is to just install [Docker Desktop](https://www.docker.com/products/docker-desktop). The select one of the options below
(via VSCode or via the shell).


## VSCode: Develop with docker via VSCode
If you just have the ``Remote - Containers`` extension (made by the vsode team), you should be asked if you want to open the project in the remote container when you open the project. If you are not asked, you
can use the ``Remote - Containers`` at the bottom left of the vscode window,
or one of the following commands in the commapdn palette:

- ``Remote-Container: Open folder in Container``
- ``Remote-Container: Rebuild and Reopen in Container``
- ``Remote-Container: Reopen in Container``

Since we have a ready-to-use configuration in ``.devcontainer/``, this should *just work*. Check out https://code.visualstudio.com/docs/remote/containers-tutorial for more details.

### VSCode: Python interpreter not found
You will get this if you have a python file open before ``pip install`` is done. Just wait for ``pip install`` to finish running (part of starting up the container),
and run ``Develop: Reload Window`` command palette action.


### VSCode: Run the development server
Start up a terminal via VSCode. This starts a terminal in the docker container. Run:
```
$ ievv devrun
```

### VSCode: Build css/javascript
Start up a terminal via VSCode. This starts a terminal in the docker container. Run:
```
$ ievv buildstatic --watch
```
(remove --watch to just build without watching)

### VSCode: Install python packages
You should not need to do this unless you have updated Pipfile since this is done when the docker container launches (configured in ``postCreateCommand`` in ``.devcontainer/devcontainer.json``).
Start up a terminal via VSCode. This starts a terminal in the docker container. Run:
```
$ pip install -r requirements/development.txt
```

### VSCode: Rebuild the docker image
Run the ``Remote-Container: Rebuild and Reopen in Container`` command palette command.


### VSCode: Connect to the docker container via terminal
You may want to open the shell in your docker container via the "normal" terminal instead of via VSCode. You can do that with:

```
$ docker ps
... find the name of the container (last column) ...
$ docker exec -it <container-name or ID> bash -c "sudo -u codemonkey -s"
... drops you into /, so do "cd /workspaces/devilry-django/" to get to the repo root ...
```

---


## CLI: Develop with docker via the shell
We have a Dockerfile with all you need for devilry-django in ``.devcontainers/Dockerfile``.

### CLI: Build the docker image with:

```
$ docker build -t devilry-django_dev .devcontainer/
```

### CLI: Run the built image

```
$ docker run -t -i --mount type=bind,src=$(pwd),dst=/workspaces/devilry-django,consistency=cached --mount source=devilry-django_dockerdev_persistent,destination=/home/codemonkey/persistent/ -w "/workspaces/devilry-django" -p 9121 -u codemonkey --name devilry-django devilry-django_dev bash
```

This starts the bash shell in the container. Run the following commands to install the required python packages and start the required servers (django devserver, postgres, redis, ...):

```
$ pip install -r requirements/development.txt
$ ievv devrun
```

**NOTE:** This shell is the process keeping the docker container running, so do not exit the bash shell. You can quit the ``ievv devrun`` command and run other commands, when you exit the bash shell, the container stops.


### CLI: Build css/javascript
Run the following command to start a shell in the docker container:
```
$ docker exec -it devilry-django bash
```
The you can build CSS and other stuff you normally do from the shell.. To build css, run:

```
$ ievv buildstatic --watch
```
(remove --watch to just build without watching)


### CLI: Rebuild the docker image
Just repeast the command used to build the docker image above.


### CLI: Mount an extra folder
Just add more ``--mount`` statements the ``docker run`` command in the *CLI: Run the built image* section above. To mount your home folder, add
```
--mount type=bind,src=$HOME,dst=/host_userhome/,consistency=cached
```
and that makes your HOME directory available as ``/host_userhome/`` within the docker container.


---

## When to rebuild the docker image?
You need to rebuild it each time you pull changes to ``.devcontainers/Dockerfile``. If you are using the VSCode integration/extension, you also have to rebuild when ``.devcontainers/devcontainer.json`` changes. How to rebuild is explained in each of the sections above.

NOTE: The VSCode plugin will often just detect this and ask you to rebuild.


## Create a database

You can create a fairly full featured demo database with:
```
$ ievv recreate_devdb
```


## Run the Django development server

Start the Django development server with:

```
$ ievv devrun
```

Go to http://localhost:8000/ and log in as a superuser using:
```
user: grandma@example.com
password: test
```

**Note:** All users have ``password==test``, and you can see all users
in the superadmin interface.



## Symlinking packages during development
Both during python and node development symlinking packages is useful (pip install -e, yarn link, npm link, ...). To be able to do that you need to have access to other code your disk. Our VSCode setup makes your HOME directory available as ``/host_userhome/``, and the *CLI: Mount an extra folder* explains how to do this with the CLI. As long as you have the code available using symlinking will be exactly as it would be done outside of docker just with ``/host_userhome/some/code/path`` instead of ``~/some/code/path``.

Example (assumes you have django_cradmin in ~/code/django_cradmin/ locally):
```
$ pip uninstall django_cradmin
$ pip install -e /host_userhome/code/django_cradmin
```


## Choices made for the docker setup
The docker setup is optimized for development. It tries to avoid having to rebuild the docker image all the time, but that comes at the cost of having to re-install all python, javascript and CSS stuff each time you "kill" the docker image. On the other hand it makes the setup fairly bulletproof since it is fairly hard to screw up and not install the correct stuff (it works or not, and is hard to get into partly working states).