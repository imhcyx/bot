import json
import os

if os.path.exists('config.json'):
    cfgfile = 'config.json'
else:
    cfgfile = 'defconfig.json'

with open(cfgfile, 'r') as f:
    cfg = json.load(f)

assert 'ws' in cfg
assert 'db' in cfg
assert 'admin_id' in cfg