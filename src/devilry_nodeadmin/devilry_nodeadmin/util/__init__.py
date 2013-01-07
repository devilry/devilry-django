from django.contrib.auth.decorators import login_required

@login_required
def emptyview(request):
    from django.http import HttpResponse
    return HttpResponse('Logged in')

class Out:
    def __init__( self, *params ):
        pass
    def __call__( self, requets, *args, **kwargs ):
        from django.http import HttpResponse
        return HttpResponse( 'Out' )
