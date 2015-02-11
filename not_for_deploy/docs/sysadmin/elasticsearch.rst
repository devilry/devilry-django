*****************************************************
Install and configure the ElasticSearch search server
*****************************************************

Install ElasticSearch
=====================
See http://www.elasticsearch.org/.


Configure ElasticSearch as the Devilry search backend
=====================================================
Add the following to ``~/devilrydeploy/devilry_settings.py``::

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'devilry',
        },
    }

Adjust the URL if you are running ElasticSearch on a separate server or another port.


Build the search index
======================
To index the data currently in the database, run::

    $ cd ~/devilrydeploy/
    $ python manage.py rebuild_index --noinput
