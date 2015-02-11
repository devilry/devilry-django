.. _nginx:

=========================================================
Configure Nginx as the Devilry webserver for static files
=========================================================

For Nginx, you should use something like this (not a complete config file, just
the location sections that you should add to your config)::

    location /static {
        # Show directory index.
        autoindex  on;

        # NOTE from: http://wiki.nginx.org/HttpCoreModule#root
        # Keep in mind that the root will still append the directory
        # to the request so that a request for "/i/top.gif" will not look
        # in "/spool/w3/top.gif" like might happen in an Apache-like alias
        # configuration where the location match itself is dropped. Use the
        # alias directive to achieve the Apache-like functionality.
        root /path/to/devilrybuild;
    }

    location / {
        proxy_pass       http://127.0.0.1:8002;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-DEVILRY_USE_EXTJS true;

        # SSL options
        proxy_set_header X-FORWARDED-PROTOCOL ssl;
        proxy_set_header X-FORWARDED-SSL on;
        proxy_headers_hash_max_size 1024;
        proxy_headers_hash_bucket_size 256;
        proxy_set_header X-Forwarded-Proto https;
    }

We recommend Nginx because it is fast, lightweight, secure and easy to setup.
