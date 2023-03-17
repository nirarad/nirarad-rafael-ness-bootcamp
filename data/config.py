import json
import dotenv
env = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../.env"))
containers = json.load(open(env["QUEUE"]))
exch = json.load(open(env["QUEUE"]))
queues = json.load(open(env["QUEUE"]))
r_key = json.load(open(env["QUEUE"]))
