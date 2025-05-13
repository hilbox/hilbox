#!/usr/bin/env python3
"""
HilBox CLI – call from CI or your laptop.

$ hilbox.py deploy  <uuid> camera_fw.py      # push new FW
$ hilbox.py ping    <uuid>                   # sanity check
$ hilbox.py call    <uuid> <method> [json]   # raw RPC
"""
import argparse, asyncio, json, sys, gzip, hashlib
from pathlib import Path
from box import Box          # same package

CHUNK = 1024

async def cmd_ping(uuid):
    async with Box(uuid) as b:
        print(await b.call("ping"))

async def cmd_call(uuid, method, param_json):
    params = json.loads(param_json or "{}")
    async with Box(uuid) as b:
        print(await b.call(method, params))

async def cmd_deploy(uuid, path):
    data  = Path(path).read_bytes()
    blob  = gzip.compress(data)
    sha   = hashlib.sha256(blob).hexdigest()
    print(f"Pushing {len(blob)} bytes  sha256={sha}")
    async with Box(uuid) as b:
        await b.ota(blob)
    print("✓ OTA complete")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("ping");   sp.add_argument("uuid")
    sp = sub.add_parser("call");   sp.add_argument("uuid"); sp.add_argument("method"); sp.add_argument("params", nargs="?")
    sp = sub.add_parser("deploy"); sp.add_argument("uuid"); sp.add_argument("file")

    args = ap.parse_args()
    coro = {"ping":   cmd_ping,
            "call":   cmd_call,
            "deploy": cmd_deploy}[args.cmd](**vars(args))
    asyncio.run(coro)

if __name__ == "__main__":
    main()
