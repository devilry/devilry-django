from django.shortcuts import render


def custom_404_handler(request, *args, **kwargs):
    response = render(
        request,
        'devilry_errortemplates/404.django.html',
        {
            'request_path': request.path
        }
    )
    response.status_code = 404
    return response


def custom_500_handler(request, *args, **kwargs):
    response = render(
        request,
        'devilry_errortemplates/500.django.html'
    )
    response.status_code = 500
    return response
