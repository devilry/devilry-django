from django.http import HttpResponse

def stricthttp(request, restapimethodname, output_content_type, encoded_output):
    print restapimethodname
    if restapimethodname == "create":
        status = 201
    else:
        status = 200
    return HttpResponse(encoded_output, content_type=output_content_type, status=status)