import sys
from optparse import make_option

def get_input_encoding():
    """ Get the input encoding used for input to management commands.

    :return: ``sys.stdin.encoding``
    """
    return sys.stdin.encoding

def make_input_encoding_option():
    """
    Make optparse ``--input-encoding`` option that should be used on management
    commands using input/output.

    ``dest`` is set to ``inputencoding``.
    """
    return make_option('--input-encoding',
                       dest='inputencoding',
                       default=get_input_encoding(),
                       help=('Input encoding. Defaults to ``sys.stdin.encoding``, '
                             'which currently is set to: {0}').format(get_input_encoding()))

def get_output_encoding():
    """ Get the output encoding used for output to management commands.

    :return: ``sys.stdout.encoding``
    """
    return sys.stdout.encoding

def make_output_encoding_option():
    """
    Make optparse ``--output-encoding`` option that should be used on
    management commands using output/output.

    ``dest`` is set to ``outputencoding``.
    """
    return make_option('--output-encoding',
                       dest='outputencoding',
                       default=get_output_encoding(),
                       help=('Input encoding. Defaults to ``sys.stdout.encoding``, '
                             'which currently is set to: {0}').format(get_output_encoding()))
