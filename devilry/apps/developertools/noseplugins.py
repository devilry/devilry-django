import os
from nose.plugins import Plugin


class AddSeleniumArgs(Plugin):
    name = 'seleniumargs'

    def options(self, parser, env=os.environ):
        super(AddSeleniumArgs, self).options(parser, env=env)
        parser.add_option("-b", "--selenium-browser", dest="seleniumbrowser",
                          help="Selenium browser. One of: 'Chrome', 'Firefox', 'Ie'. Defaults to 'Chrome'.",
                          metavar="BROWSER",
                          default='Chrome')

    def configure(self, options, conf):
        super(AddSeleniumArgs, self).configure(options, conf)
        if not self.enabled:
            return
        self.seleniumbrowser = options.seleniumbrowser

    def prepareTestCase(self, test):
        setattr(test.test, 'seleniumbrowser', self.seleniumbrowser)
