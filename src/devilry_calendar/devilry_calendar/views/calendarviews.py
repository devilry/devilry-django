from django.views.generic import TemplateView

class CalendarView(TemplateView):
    template_name = "devilry_calendar/calendar.django.html"