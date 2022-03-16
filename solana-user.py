import time
import json
import random
from locust import HttpUser, task, between
from locust.exception import StopUser

program_keys = ["Stake11111111111111111111111111111111111111", "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin", "mv3ekLzLbnVPNxjSKvqBpU3ZeZXPQdEC3bp5MDEBG68"]

# Base class for Solana 
class SolanaUser(HttpUser):
  wait_time = between(0.1,1)
  abstract = True

  def get_req_json(self, method, params=[]):
    req =  {"jsonrpc":"2.0","id":1,"method":method}
    if len(params) > 0:
      req["params"] = params
    return json.dumps(req)

  def rpc(self, method, params=[], methodSuffix=""):
   with self.client.post('/', data=self.get_req_json(method,params),  headers={'content-type': 'application/json'}, name=method+methodSuffix, catch_response=True) as response:
      try: 
        if response.text:
          json_data = response.json()
          if "error" in json_data:
            response.failure(json_data["error"]["message"])
        else:
          response.failure("Request returned empty data")
      except json.decoder.JSONDecodeError as e:
        response.failure("Invalid json returned: "+response.text+" "+str(e))
      except ValueError as e:
        response.failure("Invalid json returned: "+response.text+" "+str(e))

  def on_start(self):
    self.program_key = random.choice(program_keys)

# Heavy calls
class SlowCalls(SolanaUser):
  weight = 1

  @task
  def get_leader_schedule(self):
    self.rpc("getLeaderSchedule")

  @task
  def get_largest_accounts(self):
    self.rpc("getLargestAccounts")

  @task
  def get_program_accounts(self):
    self.rpc("getProgramAccounts", [self.program_key])

# A solana explorer type user
class ExplorerUser(SolanaUser):
  weight = 10

  @task
  def get_slot(self):
    self.rpc("getSlot")

  @task
  def get_slot_leader(self):
    self.rpc("getSlotLeader")

  @task
  def get_cluster_nodes(self):
    self.rpc("getClusterNodes")

  @task
  def get_epoch_schedule(self):
    self.rpc("getEpochSchedule")

  @task
  def get_epoch_info(self):
    self.rpc("getEpochInfo")

  @task
  def minimum_ledger_slot(self):
    self.rpc("minimumLedgerSlot")

  # This triggers big table lookup
  @task
  def get_confirmed_blocks(self):
    self.rpc("getConfirmedBlocks", [5, 10], "BigTable")



