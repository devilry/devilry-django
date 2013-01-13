from django.conf import settings
from uuid import uuid1


class Registry(object):
    def __init__(self):
        self.items = {}

    def add(self, id, title, description, url, settingssaver=None):
        self.items[id] = dict(title=title, description=description, url=url,
            settingssaver=settingssaver)

    def __contains__(self, pluginid):
        return pluginid in self.items

    def get_configured_list(self):
        items = []
        for id in settings.DEVILRY_QUALIFIESFOREXAM_PLUGINS:
            item = self.items[id]
            items.append({
                'id': id,
                'title': unicode(item['title']),
                'description': unicode(item['description']),
#                'pluginsessionid': 'test',
                'pluginsessionid': uuid1().hex,
                'url': str(item['url'])
            })
        return items

    def has_settingssaver(self, pluginid):
        return self.items[pluginid]['settingssaver'] != None

    def save_settings_for(self, status, settings):
        self.items[status.plugin]['settingssaver'](status, settings)

    def unregister(self, pluginid):
        del self.items[pluginid]

qualifiesforexam_plugins = Registry()