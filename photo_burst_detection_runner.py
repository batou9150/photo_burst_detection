#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from photo_burst_detection import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.basicConfig(level=logging.DEBUG)
    app.logger = logging.Logger('main')
    app.run(debug=True, use_debugger=True, use_reloader=True, passthrough_errors=True, host='0.0.0.0', port=port)
