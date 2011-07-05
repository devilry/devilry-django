from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from restful import RestStatConfig, RestPeriodPoints


@login_required
def main(request):
    return render(request,
        'tutorialstats/main.django.html', {
            'RestStatConfig': RestStatConfig,
            'RestPeriodPoints': RestPeriodPoints
        })
