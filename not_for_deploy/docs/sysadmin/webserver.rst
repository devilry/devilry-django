###########################################################
Setup Nginx, Apache or some other web proxy server with SSL
###########################################################

You need to configure your webserver to act as a reverse proxy that
forwards all traffic from port 443 (the https port) to ``127.0.0.0:8002``.

The webserver must use SSL, and it should redirect traffic from port 80 to port 443.

Refer to the Gunicorn_ documentation for more information.



********************
Nginx config example
********************
.. code-block:: nginx

    server {
       listen 80;
       server_name devilry.example.com;
       return 301 https://$server_name$request_uri;
    }

    server {
       listen 443 ssl default_server;
       server_name devilry.example.com;

       ssl_certificate /path/to/certificate.pem;
       ssl_certificate_key /path/to/certificate-key.key;

       ssl_session_timeout 5m;
       ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
       ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
       ssl_prefer_server_ciphers on;
       ssl_session_cache shared:SSL:10m;
       ssl_dhparam /path/to/diffie-hellman-parameter.pem;

       # let nginx server static content ...
       location /staticfiles/ {
          autoindex on;
          root /path/to/directory/;
       }

       # ... while gunicorn handles the rest
       location / {
          proxy_pass http://127.0.0.1:8002;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto https;
       }
    }


.. _Gunicorn: http://gunicorn.org/
