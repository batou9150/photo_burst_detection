#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import secrets

# development only: a throwaway key, inherited by the reloader's child process
os.environ.setdefault('SECRET_KEY', secrets.token_hex())

from photo_burst_detection import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # the Werkzeug debugger allows code execution: only listen on localhost unless HOST is set explicitly
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    logging.basicConfig(level=logging.DEBUG)
    app.logger = logging.Logger('main')
    app.run(debug=debug, use_debugger=debug, use_reloader=debug, passthrough_errors=debug, host=host, port=port)
