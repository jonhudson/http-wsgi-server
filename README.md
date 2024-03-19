# http-wsgi-server
A Python HTTP WSGI Server

**This is a toy project** for fun and learning. It is nowhere near complete and possibly never will be. 

    python -m venv .venv
    . .venv/bin/activate
    pip install -e .
    python -m httpwsgiserver 127.0.0.1:9000 'module:app'

Assuming `module` is a Python module that contains a WSGI callable named `app`.
