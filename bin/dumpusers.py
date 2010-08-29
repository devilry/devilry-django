#!/usr/bin/env python

import sys

from django.contrib.auth.models import User


for line in sys.stdin:
    l = [x.strip() for x in line.split("::", 2)]
        if len(l) > 1:
            kw = {}
            kw['username'] = l[0]

u = User(
        username = 'espeak',
        email = 'espeak@example.com',
        first_name = 'Espen',
        last_name = 'Kristiansen',
        is_active = True,
        is_staff = False,
        is_superuser = False)
u.save()
