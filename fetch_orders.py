import asyncio as aio
import json
import time
from types import SimpleNamespace
from webSocket import WebSocket

parsejson = lambda s: json.loads(s, object_hook=lambda d: SimpleNamespace(**d))


def readfile(path):
    with open(path) as f:
        return parsejson(f.read())


from_ts = None
creds = None
oa = None
pt = None
_ws = None
_closed = None


def construct_msg(payloadType, fields=None, clientMsgId=None):
    if fields is None:
        fields = {}

    msg = {
        "payloadType": payloadType,
        "payload": {
            "ctidTraderAccountId": creds.accountId,
            "accessToken": creds.accessToken,
            **fields
        }
    }

    if clientMsgId:
        msg["clientMsgId"] = clientMsgId

    return json.dumps(msg)


async def on_ready(ws):
    print("✅ account authenticated – ready")

    msg = construct_msg(pt.req.OrderList, {
        'fromTimestamp': from_ts,
        'toTimestamp': int(time.time() * 1000)
    })
    await ws.send(msg)


async def on_resp(ws, msg_str):
    msg = json.loads(msg_str)
    payloadType = msg["payloadType"]
    payload = msg["payload"]

    if payloadType == pt.res.OrderList:
        with open("data/orders.json", "w") as f:
            json.dump(payload["order"], f, indent=2)
        print("📁 written to orders.json")
        await ws.close()
    else:
        print("unknown payloadType:")
        print(msg_str)

async def _on_open():
    print("🔌 connected")

    msg = {
        "payloadType": pt.req.ApplicationAuth,
        "payload": {
            "clientId": creds.clientId,
            "clientSecret": creds.clientSecret
        }
    }
    await _ws.send(json.dumps(msg))


async def _on_message(msg_str):
    msg = parsejson(msg_str)

    if msg.payloadType == pt.res.ApplicationAuth:
        print("🔐 application authenticated")
        await _ws.send(construct_msg(pt.req.AccountAuth))
        return

    if msg.payloadType == pt.res.AccountAuth:
        print("🔐 account authenticated")
        await on_ready(_ws)
        return

    if msg.payloadType == pt.common.HeartbeatEvent:
        await _ws.send(json.dumps({"payloadType": pt.common.HeartbeatEvent}))
        return

    await on_resp(_ws, msg_str)


async def _on_close():
    print("❌ connection closed")
    _closed.set()


async def _on_error(err):
    print("⚠️ websocket error:", err)
    _closed.set()


async def fetch(from_when):
    global creds, oa, pt, _ws, _closed, from_ts

    from_ts = from_when

    creds = readfile("./credentials.json")
    oa = readfile("models/OAModel.custom.json")
    pt = readfile("models/payloadTypes.custom.json")

    _closed = aio.Event()
    _ws = WebSocket("wss://live.ctraderapi.com:5036")

    _ws.onopen = _on_open
    _ws.onmessage = _on_message
    _ws.onclose = _on_close
    _ws.onerror = _on_error

    await _closed.wait()
