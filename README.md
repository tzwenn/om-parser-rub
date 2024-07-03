# OpenMensa Parser for RUB canteens

Parses AKAFÖ and Q-West websites and prepares a canteen feed for [OpenMensa](https://openmensa.org).

Sources used:

* https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/ruhr-universitaet-bochum/
* https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/rote-bete/
* https://www.akafoe.de/gastronomie/speiseplaene-der-mensen/hochschule-bochum/
* https://q-we.st/speiseplan/

## Usage

1. Clone, setup venv, install requirements.txt ...
2. You can use `make debug` for development which starts a dedicated flask debug server

## Installation

This WSGI-App needs to run on a publicly accessible URL to be found by the OpenMensa feed collector.
You can use, e.g., [Gunicorn](https://gunicorn.org/) + unix socket + systemd + nginx like this:

#### Nginx file

```
server {
    server_name om-parser-rub.tld;

    listen [::]:443 ssl;
    listen 443 ssl;

    # [...]
    #--------------------------------------------------------------------

     location / {
        proxy_set_header Host            $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/om-rub/om-rub.sock;
    }

    #--------------------------------------------------------------------
}
```

### Systemd service file

```
[Unit]
Description=Gunicorn instance to serve OpenMensa RUB feed
After=network.target

[Service]
WorkingDirectory=<path-to>/om-parser-rub
RuntimeDirectory=om-rub
RuntimeDirectoryMode=755
User=om-rub
Group=http
ExecStart=<path-to>/om-parser-rub/venv/bin/gunicorn --workers 1 --bind unix:/run/om-rub/om-rub.sock -u om-rub -g http -m 007 rub.wsgi:app

[Install]
WantedBy=multi-user.target
```