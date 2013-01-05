from django.conf import settings



class Registry(object):
    def __init__(self):
        self.items = {}

    def add(self, id, title, description, url):
        self.items[id] = dict(title=title, description=description, url=url)

    def get_configured_list(self):
        items = []
        for id in settings.DEVILRY_QUALIFIESFOREXAM_PLUGINS:
            item = self.items[id]
            items.append({
                'id': id,
                'title': unicode(item['title']),
                'description': unicode(item['description']),
                'url': str(item['url'])
            })
        return items


qualifiesforexam_plugins = Registry()