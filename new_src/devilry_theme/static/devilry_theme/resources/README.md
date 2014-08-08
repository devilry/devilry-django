
# Install the required version of compass and sass

Due to some recent compass developments, we need to use a specific compass and sass version:

    $ sudo gem uninstall sass
    $ sudo gem uninstall compass
    $ sudo gem install sass -v 3.1.1
    $ sudo gem install compass -v 0.11.7

See: https://github.com/vwall/compass-twitter-bootstrap/issues/45 for more info


# Install gem on Ubuntu

    $ sudo apt-get install rubygems


# Build the theme

CD to the ``sass/`` directory and run ``compass compile`` or ``compass watch``.
