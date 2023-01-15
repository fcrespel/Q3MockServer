#!/usr/bin/python3

import argparse
import logging
import random
import socketserver
import time

DEFAULT_SERVERINFO = {
  "clients": "0",
  "fdisable": "0",
  "game": "base",
  "gametype": "0",
  "hostname": "*Jedi*",
  "mapname": "none",
  "needpass": "0",
  "protocol": "26",
  "sv_maxclients": "32",
  "truejedi": "0",
  "wdisable": "524274",
}

DEFAULT_SERVERSTATUS = {
  "bg_fighterAltControl": "0",
  "capturelimit": "0",
  "dmflags": "0",
  "duel_fraglimit": "1",
  "fraglimit": "0",
  "g_allowNPC": "1",
  "g_debugMelee": "2",
  "g_duelWeaponDisable": "1",
  "g_forceBasedTeams": "0",
  "g_forcePowerDisable": "0",
  "g_forceRegenTime": "200",
  "g_gametype": "0",
  "g_jediVmerc": "0",
  "g_maxForceRank": "7",
  "g_maxGameClients": "0",
  "g_maxHolocronCarry": "3",
  "g_needpass": "0",
  "g_noSpecMove": "0",
  "g_privateDuel": "2",
  "g_saberLocking": "0",
  "g_saberWallDamageScale": "0.4",
  "g_showDuelHealths": "0",
  "g_siegeRespawn": "20",
  "g_siegeTeam1": "none",
  "g_siegeTeam2": "none",
  "g_siegeTeamSwitch": "1",
  "g_stepSlideFix": "1",
  "g_weaponDisable": "524274",
  "gamename": "BaseJKA",
  "mapname": "none",
  "protocol": "26",
  "sv_allowDownload": "0",
  "sv_floodProtect": "0",
  "sv_hostname": "*Jedi*",
  "sv_maxclients": "32",
  "sv_maxPing": "0",
  "sv_maxRate": "0",
  "sv_minPing": "0",
  "sv_minRate": "0",
  "sv_privateClients": "0",
  "timelimit": "0",
  "version": "JAmp: v1.0.1.1 linux-i386 Nov 10 2003",
}

class Q3MockServer(socketserver.BaseRequestHandler):
  header = b"\xff\xff\xff\xff"
  logger = logging.getLogger("Q3MockServer")

  def handle(self):
    addr = self.client_address
    req_raw = self.request[0]
    self.logger.debug("<<< %s %s", addr, req_raw)
    if req_raw[0:4] == self.header:
      req = req_raw[4:].decode("ascii").strip().split()
      resp = None
      if req[0] == "getinfo":
        resp = self.getinfo(*req[1:])
      elif req[0] == "getstatus":
        resp = self.getstatus(*req[1:])
      elif req[0] == "getchallenge":
        resp = self.getchallenge(*req[1:])
      elif req[0] == "connect":
        resp = self.connect(*req[1:])
      elif req[0] == "rcon":
        resp = self.rcon(*req[1:])
      elif req[0] == "disconnect":
        pass
      else:
        self.logger.error("Invalid command from %s: %s", addr[0], req[0])
      if resp:
        resp_raw = self.header + resp.encode("ascii")
        self.logger.debug(">>> %s %s", addr, resp_raw)
        self.request[1].sendto(resp_raw, addr)
    else:
      self.logger.error("Invalid packet from %s", addr[0])

  def getinfo(self, challenge="", *args):
    self.logger.info("client challenge=%s", challenge)
    serverinfo = self.server.serverinfo.copy()
    if challenge:
      serverinfo["challenge"] = challenge
    return "infoResponse\n" + self.dict2info(serverinfo) + "\n"

  def getstatus(self, challenge="", *args):
    self.logger.info("client challenge=%s", challenge)
    serverstatus = self.server.serverstatus.copy()
    if challenge:
      serverstatus["challenge"] = challenge
    return "statusResponse\n" + self.dict2info(serverstatus) + "\n"

  def getchallenge(self, challenge="", *args):
    serverchallenge = ((random.randint(0, 32767) << 16) ^ random.randint(0, 32767)) ^ int(time.time())
    self.logger.info("client challenge=%s, server challenge=%s", challenge, serverchallenge)
    return "challengeResponse " + str(serverchallenge) + " " + challenge + "\n"

  def connect(self, userinfo="", *args):
    self.logger.info("userinfo=%s", self.info2dict(userinfo))
    return "print\n" + self.server.message + "\n"

  def rcon(self, password="", *args):
    self.logger.info("command=%s", args)
    return "print\nRcon is not supported.\n"

  def dict2info(self, d):
    info = ""
    for k, v in d.items():
      info += "\\" + k + "\\" + v
    return info

  def info2dict(self, info):
    d = {}
    kv = info.split("\\")
    for i in range(1, len(kv), 2):
      d[kv[i]] = kv[i+1]
    return d

def parse_kvps(kvps):
  d = {}
  if kvps:
    for kvp in kvps:
      kv = kvp.split("=", 1)
      d[kv[0]] = kv[1]
  return d

def parse_args():
  parser = argparse.ArgumentParser(description="Q3MockServer")
  parser.add_argument("-a", "--address", help="Address to bind to (default: 0.0.0.0)", type=str, default="0.0.0.0")
  parser.add_argument("-p", "--port", help="Port to listen on (default: 29070)", type=int, default=29070)
  parser.add_argument("-m", "--message", help="Message displayed to connecting players", type=str, default="Server currently unavailable")
  parser.add_argument("-i", "--info", help="Server info key=value pair (repeatable)", action="append")
  parser.add_argument("-s", "--status", help="Server status key=value pair (repeatable)", action="append")
  parser.add_argument("-l", "--log-level", help="Log level (default: INFO)", type=str, default="INFO", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
  return parser.parse_args()

def main():
  args = parse_args()
  logging.basicConfig(format="%(asctime)s %(levelname)5s %(process)d --- [%(name)12s] %(funcName)-12s : %(message)s", level=args.log_level)
  logging.info("Starting server")
  with socketserver.UDPServer((args.address, args.port), Q3MockServer) as server:
    server.message = args.message
    server.serverinfo = dict(DEFAULT_SERVERINFO, **parse_kvps(args.info))
    server.serverstatus = dict(DEFAULT_SERVERSTATUS, **parse_kvps(args.status))
    try:
      logging.info("Listening for commands")
      server.serve_forever()
    except KeyboardInterrupt:
      logging.info("Shutting down server")

if __name__ == "__main__":
  main()
