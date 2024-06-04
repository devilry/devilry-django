
from model_bakery import baker


class GenerateShortName(object):
    counter = 0

    def __call__(self):
        GenerateShortName.counter += 1
        return 'bakershort{}'.format(self.counter)


def generate_long_name():
    from model_bakery.utils import seq as baker_seq
    return baker_seq('Baker Long Name')


class CustomBaker(baker.Baker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        baker.generators.add('devilry.apps.core.models.custom_db_fields.ShortNameField', GenerateShortName())
        baker.generators.add('devilry.apps.core.models.custom_db_fields.LongNameField', generate_long_name)
