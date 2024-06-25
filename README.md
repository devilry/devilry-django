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

```bash
brew install pipx
pipx ensurepath
```

Then install hatch and commitizen:

```bash
pipx install hatch
pipx install commitizen
```

See https://github.com/pypa/pipx, https://hatch.pypa.io/latest/install/
and https://commitizen-tools.github.io/commitizen/ for more install alternatives if
needed, but we really recommend using pipx since that is isolated.

### Install development dependencies

#### Install a local python version with pyenv:

```bash
pyenv install 3.10
pyenv local 3.10
```

#### Install dependencies in a virtualenv:

```bash
./recreate-virtualenv.sh
```

Alternatively, create virtualenv manually (this does the same as recreate-virtualenv.sh):

```bash
python -m venv .venv
```

the ./recreate-virtualenv.sh script is just here to make creating virtualenvs more uniform
across different repos because some repos will require extra setup in the virtualenv
for package authentication etc.

#### Install dependencies in a virtualenv:

```bash
source .venv/bin/activate   # enable virtualenv
.venv/bin/pip install -e ".[dev,test,docs]"
```

### Upgrade your local packages

This will upgrade all local packages according to the constraints
set in pyproject.toml:

```bash
.venv/bin/pip install --upgrade --upgrade-strategy=eager ".[dev,test]"
```

### Run postgres and redis

```bash
docker compose up
```

### Run dev server

```bash
source .venv/bin/activate   # enable virtualenv
ievv devrun
```

### Create or re-create a devdatabase
You should always clear the database before recreating it. The easiest way is just to clear the docker resources (and volumes) and start it again.
```bash
docker compose down -v
docker compose up
```

Run dev server (in a new terminal)
```bash
source .venv/bin/activate   # activate virtualenv
ievv devrun
```

Load devdatabase SQL-file (in a new terminal)
```bash
source .venv/bin/activate   # activate virtualenv
docker compose exec -T postgres psql -U dbdev --dbname=dbdev -p 5432 -h localhost < devilry/project/develop/dumps/default.sql
python manage.py migrate
ievv customsql -i -r
```

If the dump should be updated for e.g new migrations, run the following and commit to repo:
```bash
docker compose exec -T postgres pg_dump --clean --no-owner --no-acl --no-privileges -U dbdev -h localhost -p 5432 dbdev > devilry/project/develop/dumps/default.sql
```

### Test users in the devdatabase
All users have ``test`` as their password, and the most commonly needed users are:

- Superuser: grandma@example.com
- Admin (and examiner): odin@example.com
- Examiner (and student): thor@example.com
- Student: april@example.com

You can find them all by logging in as grandma@example.com and going to http://localhost.test:8000/djangoadmin/devilry_account/user/


### Browse uploaded files
Files are stored in MinIO (S3 compatible storage that is run via docker-compose).
To browse files:

- Go to http://localhost:9001/
- Login with:
  - username: ``testuser``
  - password: ``testpassword``
- Select _Object browser_ in the sidebar.

The MinIO files is stored on disk in the ``minio_devdata`` directory in the root
of the repo, and you can stop docker compose, and just run ``rm -rf minio_devdata``
to remove all the files.


### Run tests

```bash
source .venv/bin/activate   # enable virtualenv
pytest devilry
```

### Build css/javascript:
```bash
source .venv/bin/activate   # activate virtualenv
nvm use 14    # May need to run "nvm install 14" first
ievv buildstatic
# ... or if you want to watch for changes ...:
ievv buildstatic --watch
```

To remove and reinstall all node-packages:
```bash
source .venv/bin/activate   # activate virtualenv
nvm use 14    # May need to run "nvm install 14" first
ievv buildstatic --npm-clean-node-modules
```

### Build docs
Docs are built on https://readthedocs.org/projects/devilry/ each time a branch is pushed,
but if you are making larger changes or need to debug build issues, you can build it
locally using:

```bash
sphinx-build not_for_deploy/docs/ built-docs/
```

and when the build is complete, you can open ``built-docs/index.html`` in a browser.


### Destroy postgres and redis

```bash
docker compose down -v
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


### Update docs
Create a ``not_for_deploy/docs/sysadmin/migrationguides/migrate-from-<OLDVERSION>-to-<NEWVERSION>.rst``
with update instructions for sysadmins. See the previous version for example. Skeleton:

```rst
===========================================
Migrating from <OLDVERSION> to <NEWVERSION>
===========================================


Backup database and files
#########################

BACKUP. YOUR. DATABASE. AND. FILES.


What's new?
###########

- Change 1
- Change 2


Update devilry to <NEWVERSION>
##############################

Update the devilry version to ``<NEWVERSION>`` as described in :doc:`../update`.
```

Create a ``not_for_deploy/docs/user/changelog/<NEWVERSION>.rst`` with changelog for end-users.
This is supposed to be readable/understandable by normal users. Skeleton:

```rst
.. _<NEWVERSION>changelog:

###################################
What is new in Devilry <NEWVERSION>
###################################


Fixes
#####
- Fix 1
- Fix 2

Updates/changes
###############
- Change 1
- Change 2
```


### Set version and build staticfiles

First make sure you have NO UNCOMITTED CHANGES!

Release (create changelog, increment version, build staticfiles, commit and tag the change) with:

```bash
nvm use 14
tools/release/prepare-release.py prepare --apply  # This will bump the version and then build and commit staticfiles.
git push && git push --tags
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
hatch build -t sdist
hatch publish
rm dist/*              # optional cleanup
```
