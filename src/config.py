import json
import os

if os.path.exists('config.json'):
    cfgfile = open('config.json', 'r')
else:
    cfgfile = open('defconfig.json', 'r')

cfg = json.load(cfgfile)

cfgfile.close()