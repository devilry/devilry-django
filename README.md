# devilry

## Develop

Requires:

- https://github.com/pyenv/pyenv
- Docker (Docker desktop or similar)

### Use conventional commits for GIT commit messages

See https://www.conventionalcommits.org/en/v1.0.0/.
You can use this git commit message format in many different ways, but the easiest is:

- Use commitizen: https://commitizen-tools.github.io/commitizen/commit/
- Use an editor extension, like https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits for VScode.
- Just learn to write the format by hand (can be error prone to begin with, but it is fairly easy to learn).

### Install hatch and commitizen

NOTE: You only need hatch if you need to build releases, and you
only need commitizen for releases OR to make it easy to follow
conventional commits for your commit messages
(see _Use conventional commits for GIT commit messages_ above).

First install pipx with:

```
$ brew install pipx
$ pipx ensurepath
```

Then install hatch and commitizen:

```
$ pipx install hatch
$ pipx install commitizen
```

See https://github.com/pypa/pipx, https://hatch.pypa.io/latest/install/
and https://commitizen-tools.github.io/commitizen/ for more install alternatives if
needed, but we really recommend using pipx since that is isolated.

### Install development dependencies

#### Install a local python version with pyenv:

```
$ pyenv install 3.10
$ pyenv local 3.10
```

#### Install dependencies in a virtualenv:

```
$ ./recreate-virtualenv.sh
```

Alternatively, create virtualenv manually (this does the same as recreate-virtualenv.sh):

```
$ python -m venv .venv
```

the ./recreate-virtualenv.sh script is just here to make creating virtualenvs more uniform
across different repos because some repos will require extra setup in the virtualenv
for package authentication etc.

#### Install dependencies in a virtualenv:

```
$ source .venv/bin/activate   # enable virtualenv
$ pip install -e ".[dev,test]"
```

### Upgrade your local packages

This will upgrade all local packages according to the constraints
set in pyproject.toml:

```
$ pip install --upgrade --upgrade-strategy=eager ".[dev,test]"
```

### Run postgres and redis

```
$ docker-compose up
```

### Run dev server

```
$ source .venv/bin/activate   # enable virtualenv
$ ievv devrun
```

### Create or re-create a devdatabase
You should always clear the database before recreating it. The easiest way is just to clear the docker resources (and volumes) and start it again.
```
$ docker-compose down -v
$ docker-compose up
```

Run dev server (in a new terminal)
```
$ source .venv/bin/activate   # activate virtualenv
$ ievv devrun
```

Load devdatabase SQL-file (in a new terminal)
```
$ source .venv/bin/activate   # activate virtualenv
$ docker-compose exec -T postgres psql -U dbdev --dbname=dbdev -p 5432 -h localhost < devilry/project/develop/dumps/default.sql
$ python manage.py migrate
$ ievv customsql -i -r
```

If the dump should be updated for e.g new migrations, run the following and commit to repo:
```
$ docker-compose exec -T postgres pg_dump --clean --no-owner --no-acl --no-privileges -U dbdev -h localhost -p 5432 dbdev > devilry/project/develop/dumps/default.sql
```

### Run tests

```
$ source .venv/bin/activate   # enable virtualenv
$ pytest devilry
```

### Build css/javascript:
```
$ source .venv/bin/activate   # activate virtualenv
$ nvm use 14    # May need to run "nvm install 14" first
$ ievv buildstatic
... or if you want to watch for changes ...:
$ ievv buildstatic --watch
```

To remove and reinstall all node-packages:
```
$ source .venv/bin/activate   # activate virtualenv
$ nvm use 14    # May need to run "nvm install 14" first
$ ievv buildstatic --npm-clean-node-modules
```

### Destroy postgres and redis

```
$ docker-compose down -v
```

## Documentation

https://devilry.readthedocs.io

## Release

### Translations

To translate new texts, do the following:

- ``ievv makemessages``
- Translate the .po files. Poedit is a great tool for this.
- ``ievv compilemessages``
- Commit the changes

### Set version and build staticfiles

First make sure you have NO UNCOMITTED CHANGES!

Release (create changelog, increment version, build staticfiles, commit and tag the change) with:

```bash
$ nvm use 14
$ tools/release/prepare-release.py prepare --apply  # This will bump the version and then build and commit staticfiles.
$ git push && git push --tags
```

### NOTE (release):

- `cz bump` automatically updates CHANGELOG.md, updates version file(s), commits the change and tags the release commit.
- If you are unsure about what `cz bump` will do, run it with `--dry-run`. You can use
  options to force a specific version instead of the one it automatically selects
  from the git log if needed, BUT if this is needed, it is a sign that someone has messed
  up with their conventional commits.
- `cz bump` only works if conventional commits (see section about that above) is used.
- `cz bump` can take a specific version etc, but it automatically select the correct version
  if conventional commits has been used correctly. See https://commitizen-tools.github.io/commitizen/.
- If you need to add more to CHANGELOG.md (migration guide, etc), you can just edit
  CHANGELOG.md after the release, and commit the change with a `docs: some useful message`
  commit.
- The `cz` command comes from `commitizen` (install documented above).

### What if the release fails?

See _How to revert a bump_ in the [commitizen FAQ](https://commitizen-tools.github.io/commitizen/faq/#how-to-revert-a-bump).


### Migrationguide and changelog (for official readthedocs)
- Add a migration guide to not_for_deploy/docs/sysadmin/migrationguides/
- Add a changelog to not_for_deploy/docs/user/changelog/

### Release to pypi:

```bash
$ hatch build -t sdist
$ hatch publish
$ rm dist/*              # optional cleanup
```
