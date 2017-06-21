import sys
from optparse import make_option

DEFAULT_ENCODING = 'utf-8'

def get_input_encoding():
    """ Get the input encoding used for input to management commands.

    :return: ``sys.stdin.encoding``
    """
    return sys.stdin.encoding or sys.getdefaultencoding() or DEFAULT_ENCODING

def make_input_encoding_option():
    """
    Make optparse ``--input-encoding`` option that should be used on management
    commands using input/output.

    ``dest`` is set to ``inputencoding``.
    """
    return make_option('--input-encoding',
                       dest='inputencoding',
                       default=get_input_encoding(),
                       help=('Input encoding. Defaults to ``sys.stdin.encoding``, falling back '
                             'to ``sys.getdefaultencoding()`` and back to utf-8 if both are undefined. '
                             'It is currently is set to: {0}').format(get_input_encoding()))


def add_input_encoding_argument(parser):
    """
    Add argparse ``--input-encoding`` option that should be used on management
    commands using input/output.

    ``dest`` is set to ``inputencoding``.
    """
    return parser.add_argument(
        '--input-encoding',
        dest='inputencoding',
        default=get_input_encoding(),
        help=('Input encoding. Defaults to ``sys.stdin.encoding``, falling back '
              'to ``sys.getdefaultencoding()`` and back to utf-8 if both are undefined. '
              'It is currently is set to: {0}').format(get_input_encoding()))


def get_output_encoding():
    """ Get the output encoding used for output to management commands.

    :return: ``sys.stdout.encoding``
    """
    return sys.stdin.encoding or sys.getdefaultencoding() or DEFAULT_ENCODING


def make_output_encoding_option():
    """
    Make optparse ``--output-encoding`` option that should be used on
    management commands using output/output.

    ``dest`` is set to ``outputencoding``.
    """
    return make_option('--output-encoding',
                       dest='outputencoding',
                       default=get_output_encoding(),
                       help=('Output encoding. Defaults to ``sys.stdout.encoding``, falling back '
                             'to ``sys.getdefaultencoding()`` and back to utf-8 if both are undefined. '
                             'It is currently is set to: {0}').format(get_output_encoding()))


def add_output_encoding_argument(parser):
    """
    Add argparse ``--output-encoding`` option that should be used on
    management commands using output/output.

    ``dest`` is set to ``outputencoding``.
    """
    return parser.add_argument(
        '--output-encoding',
        dest='outputencoding',
        default=get_output_encoding(),
        help=('Output encoding. Defaults to ``sys.stdout.encoding``, falling back '
              'to ``sys.getdefaultencoding()`` and back to utf-8 if both are undefined. '
              'It is currently is set to: {0}').format(get_output_encoding()))
