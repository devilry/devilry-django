import hmac
import hashlib
from datetime import datetime
from simple_rest.auth.decorators import request_passes_test
from simple_rest.utils.decorators import wrap_object




#def get_secret_key(request, *args, **kwargs):
    # TODO:
    # return request.user.secret_key
    #return 'test'


def authentication_required(obj):
    """
    Requires that the user be authenticated either by a signature or by
    being actively logged in.
    """
    def test_func(request, *args, **kwargs):
        #secret_key = get_secret_key(request, *args, **kwargs)
        #return validate_signature(request, secret_key) or request.user.is_authenticated()
        return request.user.is_authenticated()

    decorator = request_passes_test(test_func)
    return wrap_object(obj, decorator)



def calculate_signature(key, data, timestamp):
    """
    Calculates the signature for the given request data.
    """
    # Construct the message from the timestamp and the data in the request
    message = str(timestamp) + ''.join("%s%s" % (k,v) for k,v in sorted(data.items()))

    # Calculate the signature (HMAC SHA512) according to RFC 2104
    signature = hmac.HMAC(str(key), message, hashlib.sha512).hexdigest()

    return signature




def validate_signature(request, secret_key):
    """
    Validates the signature associated with the given request.
    """

    # Extract the request parameters according to the HTTP method
    data = request.GET.copy()
    if request.method != 'GET':
        message_body = getattr(request, request.method, {})
        data.update(message_body)

    # Make sure the request contains a signature
    if data.get('sig', False):
        sig = data['sig']
        del data['sig']
    else:
        return False

    # Make sure the request contains a timestamp
    if data.get('t', False):
        timestamp = int(data.get('t', False))
        del data['t']
    else:
        return False

    # Make sure the signature has not expired
    delta = datetime.utcnow() - datetime.utcfromtimestamp(timestamp)
    if delta.seconds > 5 * 60:  # If the signature is older than 5 minutes, it's invalid
        return False

    # Make sure the signature is valid
    return sig == calculate_signature(secret_key, data, timestamp)




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
