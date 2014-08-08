#!/usr/bin/env python
# Make an example database. Clears the current database.


from devilry.apps.core.testhelpers import TestHelper
from common import depends, Command, require_djangoproject


require_djangoproject()
depends(Command('init_exampledb'),
        Command('load_grandmauser'))

testhelper = TestHelper()
testhelper.load_generic_scenario()
