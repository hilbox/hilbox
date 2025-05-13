# HilBox firmware core – MicroPython 1.24+
import socket, struct, uasyncio as aio, os, ubinascii, machine
import cbor2, uhashlib
from esp32 import NVS
import mdns

PORT             = 1337
RPC_CH, OTA_CH   = 0, 1
ACK              = b"AOK"
CHUNK            = 1024
UUID_KEY         = "uuid"

class FW:
    def __init__(self, port=PORT):
        self.port=port
        self.nvs  = NVS("box")
        self.uuid = self._ensure_uuid()
        self.rpc_table={}
        self._ota_reset()

    # -------- identity / mDNS --------
    def _ensure_uuid(self):
        b=self.nvs.get_blob(UUID_KEY)
        if not b:
            b=os.urandom(16); self.nvs.set_blob(UUID_KEY,b)
        mdns.start("hilbox-"+ubinascii.hexlify(b)[:6].decode())
        mdns.add_service("_hilbox","_udp",self.port,{"uuid":ubinascii.hexlify(b).decode()})
        return b

    # -------- RPC decorators --------
    def rpc(self, fn):
        self.rpc_table[fn.__name__]=fn
        return fn

    # -------- OTA helpers --------
    def _ota_reset(self):
        self._buf=bytearray(); self._exp=0; self._sha=None

    def _handle_ota(self, seq, body, addr):
        if seq==0:                                   # control
            meta=cbor2.loads(body)
            if meta["cmd"]=="BEGIN":
                self._exp, self._sha = meta["size"], meta["sha"]; self._buf=bytearray()
            elif meta["cmd"]=="END":
                ok = (len(self._buf)==self._exp and
                      uhashlib.sha256(self._buf).digest()==self._sha)
                if ok:
                    with open("/app.gz","wb") as f: f.write(self._buf)
                    self._ack(seq,addr); machine.reset()
                else: self._ota_reset()
        else:                                        # data
            self._buf.extend(body)
        self._ack(seq,addr)

    def _ack(self, seq, addr):
        pkt=ACK+struct.pack(">H",seq); self.sock.sendto(pkt,addr)

    # -------- run loop --------
    async def _loop(self):
        while True:
            try:
                pkt,addr=self.sock.recvfrom(1500)
                ch=pkt[0]; body=pkt[1:]
                if ch==RPC_CH:
                    req=cbor2.loads(body); meth=req["m"]; params=req.get("p",{})
                    out=self.rpc_table[meth](**params)
                    self.sock.sendto(bytes([RPC_CH])+cbor2.dumps(out),addr)
                elif ch==OTA_CH:
                    seq=struct.unpack(">H",body[:2])[0]
                    self._handle_ota(seq,body[2:],addr)
            except OSError:
                await aio.sleep_ms(10)

    def serve(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); self.sock.bind(("0.0.0.0",self.port)); self.sock.setblocking(False)
        aio.run(self._loop())
