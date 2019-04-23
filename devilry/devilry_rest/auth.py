import hmac
import hashlib
from datetime import datetime
from simple_rest.auth.decorators import request_passes_test
from simple_rest.utils.decorators import wrap_object



def get_secret_key(request, *args, **kwargs):
    public_key = request.GET.get('_auth_public_key')
    if public_key:
        #user = User.objects.get(public_key=public_key)
        #return user.secret_key
        return 'test123'
    else:
        return None


def authentication_required(obj):
    """
    Requires that the user be authenticated either by a signature or by
    being actively logged in.
    """
    def test_func(request, *args, **kwargs):
        #secret_key = get_secret_key(request, *args, **kwargs)
        #if secret_key:
            #return validate_signature(request, secret_key)
        #else:
        return request.user.is_authenticated

    decorator = request_passes_test(test_func)
    return wrap_object(obj, decorator)



def calculate_signature(secret_key, getdata, request_body):
    """
    Calculates the signature for the given request ``getdata`` and
    ``request_body``.

    Sort QUERYSTRING (``getdata``) alphabetically by key, and join all key
    value pairs into one long string. Then append the ``request_body``. This
    is the message sent to HMAC.

    Generate a signature using HMAC with ``secret_key`` as the ``key``,
    the message as the data and SHA512 as the hash function. The hexdigested
    output is the signature.
    """
    # Construct the message from the timestamp and the data in the request
    message = '{}{}{}'.format(
            ''.join("{}{}".format(k,v) for k, v in sorted(iter(getdata.items()))),
            request_body)

    # Calculate the signature (HMAC SHA512) according to RFC 2104
    signature = hmac.HMAC(str(secret_key), message, hashlib.sha512).hexdigest()

    return signature




def validate_signature(request, secret_key):
    """
    Validates the signature associated with the given request.
    """

    getdata = request.GET.copy()

    # Make sure the request contains a signature
    if getdata.get('_auth_signature', False):
        signature = getdata['_auth_signature']
        del getdata['_auth_signature']
    else:
        return False

    # Make sure the request contains a timestamp
    if getdata.get('_auth_timestamp', False):
        timestamp = int(getdata.get('_auth_timestamp', False))
    else:
        return False

    # Make sure the signature has not expired
    delta = datetime.utcnow() - datetime.utcfromtimestamp(timestamp)
    if delta.seconds > 5 * 60:  # If the signature is older than 5 minutes, it's invalid
        return False

    # Make sure the signature is valid
    request_body = request.body
    return signature == calculate_signature(secret_key, getdata, request_body)




def signature_required(secret_key_func):
    """
    Requires that the request contain a valid signature to gain access
    to a specified resource.
    """
    def actual_decorator(obj):

        def test_func(request, *args, **kwargs):
            secret_key = secret_key_func(request, *args, **kwargs)
            return validate_signature(request, secret_key)

        decorator = request_passes_test(test_func)
        return wrap_object(obj, decorator)

    return actual_decorator
