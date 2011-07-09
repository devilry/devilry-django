
class Page(object):
    def __init__(self, fields=[]):
        self.fields = fields

class Wizard(object):
    def __init__(self, title, description, *pages):
        self.title = title
        self.description = description
        self.pages = pages

class Wizards(object):
    def __init__(self, *wizards):
        self.wizards = wizards

    #def create_djangoform(self):
        #for field in self.
            #fieldsplit = field.split('__')
            #if len(fieldsplit) > 1 and fieldsplit[1] == 'id': # foreign key
                    #editablefields.append(fieldsplit[])
