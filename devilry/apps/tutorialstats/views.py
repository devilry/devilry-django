from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from restful import RestStatConfig


@login_required
def main(request):
    return render(request,
        'devilry/tutorialstats/main.html', {
            'RestStatConfig': RestStatConfig
        })
