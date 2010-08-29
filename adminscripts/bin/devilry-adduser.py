#!/usr/bin/env python

from optparse import OptionParser

from django.contrib.auth.models import User



p = OptionParser(usage="%prog [options] <username>")
p.add_option("--first-name", dest="first_name", default=None,
        help="First name", metavar="FIRSTNAME")
p.add_option("--last-name", dest="last_name", default=None,
        help="Last name", metavar="LASTNAME")
p.add_option("--email", dest="email", default=None,
        help="Email address", metavar="EMAIL")
p.add_option("--superuser", dest="superuser", default=None,
        metavar = 'yes/no',
        help="Make the user a superuser. A superuser has access to " \
                "everything in the system.")
p.add_option("--modify",
        action="store_true", dest="modify", default=False,
        help="Modify existing user instead of adding a new user.")
p.add_option("--info",
        action="store_true", dest="info", default=False,
        help="Show info about the user. No changes is made to the user.")

(opt, args) = p.parse_args()


if len(args) != 1:
    p.print_help()
    raise SystemExit()

username = args[0]
kw = {}
for x in 'first_name', 'last_name', 'email':
    value = getattr(opt, x)
    if value:
        kw[x] = value
if opt.superuser != None:
    kw['is_superuser'] = opt.superuser == 'yes'

if opt.info:
    u = User.objects.get(username=username)
    for key, label in (
            ('username', 'Username'),
            ('first_name', 'First name'),
            ('last_name', 'Last name'),
            ('email', 'Email'),
            ('is_superuser', 'Is superuser')):
        print '%s: %s' % (label, getattr(u, key))
elif opt.modify:
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        print 'ERROR: User "%s" does not exist.' % username
        raise SystemExit()
    for key, value in kw.iteritems():
        setattr(u, key, value)
    u.save()
    print 'User "%s" modified successfully.' % username
else:
    if User.objects.filter(username=username).count() == 0:
        u = User(
                username = username,
                is_active = True,
                is_staff = False,
                is_superuser = False,
                **kw)
        u.save()
        print 'User "%s" created successfully.' % username
    else:
        print 'ERROR: User "%s" already exists.' % username
        raise SystemExit()
