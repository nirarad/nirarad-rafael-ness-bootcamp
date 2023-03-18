import json
import ast
import dotenv
env = dotenv.dotenv_values(dotenv_path=dotenv.find_dotenv("../.env"))
containers = json.load(open(env["CONTAINERS"]))
exch = json.load(open(env["EXCH"]))
queues = json.load(open(env["QUEUE"]))
r_key = json.load(open(env["R_KEY"]))

