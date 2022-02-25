from django.templatetags.static import static

import devilry


def get_devilry_theme3_dist_path():
    return static('devilry_theme3/{}'.format(devilry.__version__))
