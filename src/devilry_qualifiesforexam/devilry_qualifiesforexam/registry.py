from django.conf import settings
from uuid import uuid1


class Registry(object):
    def __init__(self):
        self.items = {}

    def add(self, id, title, description, url, post_statussave=None,
            uses_settings=False, pluginsettings_summary_generator=None):
        self.items[id] = dict(title=title, description=description, url=url,
            post_statussave=post_statussave, uses_settings=uses_settings,
            pluginsettings_summary_generator=pluginsettings_summary_generator
        )

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

    def uses_settings(self, pluginid):
        return self.items[pluginid]['uses_settings']


    def has_post_statussave(self, status):
        return self.items[status.plugin]['post_statussave'] != None

    def post_statussave(self, status, settings):
        self.items[status.plugin]['post_statussave'](status, settings)

    def get_pluginsettings_summary(self, status):
        item = self.items[status.plugin]
        generator = item['pluginsettings_summary_generator']
        if generator:
            return generator(status)
        else:
            return None

    def get_title(self, pluginid):
        return self.items[pluginid]['title']

    def get_description(self, pluginid):
        return self.items[pluginid]['description']

    def unregister(self, pluginid):
        del self.items[pluginid]

qualifiesforexam_plugins = Registry()
