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

```
$ source .venv/bin/activate   # activate virtualenv
$ ievv devrun
... in a new terminal ...
$ DOES NOT EXIST YET: python manage.py devilry_develop_generate_data
```

> NOTE: Use `docker-compose down -v`, start up docker-compose again with `docker-compose up`,
> and run the management script again to recreate the devdatabase.

### Run tests

```
$ source .venv/bin/activate   # enable virtualenv
$ pytest devilry
```

### Destroy postgres and redis

```
$ docker-compose down -v
```

## Documentation

http://ievv-opensource.readthedocs.org/

## How to release devilry

First make sure you have NO UNCOMITTED CHANGES!

Release (create changelog, increment version, commit and tag the change) with:

```
$ cz bump
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

### Release to pypi:

```
$ hatch build -t sdist
$ hatch publish
$ rm dist/*              # optional cleanup
```
