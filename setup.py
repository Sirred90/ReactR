import json

# Simple script that generates config file
config = {}
config['bot_token'] = "BOT_TOKEN"

f = open('config.json', 'w')
f.write(json.dumps(config, indent = 2))
f.close