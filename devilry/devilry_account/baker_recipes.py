from django.contrib.auth.hashers import make_password

from model_bakery.recipe import Recipe


#: Use this Recipe to create users with their password set to "test".
#:
#: Example usage::
#:
#:    user = baker.make_recipe('devilry.devilry_account.user')
#:    self.assertTrue(user.check_password('test'))
from devilry.devilry_account.models import User

user = Recipe(
    User,
    password=make_password('test'))
