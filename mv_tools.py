# !/usr/bin/env python3
""" This script comes with no warranty use at your own risk
    It requires Rubrik_CDM
"""

import rubrik-cdm
import json
import urllib3
import base64

# import sh
#import os
urllib3.disable_warnings()

with open('config.json') as config_file:
    config = json.load(config_file)







