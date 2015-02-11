*****************************************************
Install and configure the ElasticSearch search server
*****************************************************

Install ElasticSearch
=====================
See http://www.elasticsearch.org/.


Configure ElasticSearch as the Devilry search backend
=====================================================
Add the following to ``~/devilrydeploy/devilry_settings.py``::

    HAYSTACK_CONNECTIONS = {  # Elastisearch
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'devilry',
        },
    }

Adjust the URL if you are running ElasticSearch on a separate server or another port.
