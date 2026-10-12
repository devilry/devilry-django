from django.conf import settings
from django.contrib.auth import logout


def cradmin_logoutview(request, template_name="cradmin_authenticate/logout.django.html"):
    next_page = None
    if "next" in request.GET:
        next_page = request.GET["next"]
    return logout(
        request, template_name=template_name, next_page=next_page, extra_context={"LOGIN_URL": settings.LOGIN_URL}
    )
