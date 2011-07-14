#!/usr/bin/env python

from devilryclient.restfulclient import login

#getpass module
#username as argument, prompt for password
#create logincookie and save it in .devilry folder

logincookie = login('http://localhost:8000/authenticate/login',
        username='grandma', password='test')
