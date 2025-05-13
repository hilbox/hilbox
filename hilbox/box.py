import asyncio, socket, struct, hashlib, gzip
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
import cbor2

MDNS_SVC  = "_hilbox._udp.local."
PORT_FALLBACK = 1337
RPC_CH, OTA_CH = 0, 1
ACK = b"AOK"
CHUNK = 1024
TIMEOUT = 3.0

class _Resolver:
    def __init__(self, uuid):
        self.uuid, self.addr = uuid, None
        Zeroconf().add_service_listener(
            MDNS_SVC, ServiceBrowser, handlers=self._hook)

    def _hook(self, zc, t, name, st):
        if st is not ServiceStateChange.Added: return
        info = zc.get_service_info(t, name)
        if not info: return
        txt = dict(info.properties)
        if txt.get(b"uuid", b"").decode() != self.uuid: return
        ip   = info.parsed_addresses()[0]
        port = info.port or PORT_FALLBACK
        self.addr = (ip, port)

async def _wait_for(fn, *a, max_ms=3000, poll=0.1):
    for _ in range(int(max_ms/(poll*1000))):
        rv = fn(*a)
        if rv: return rv
        await asyncio.sleep(poll)
    raise TimeoutError("resolver timeout")

class Box:
    """Async context-manager around one HilBox unit."""
    def __init__(self, uuid): self.uuid = uuid

    async def __aenter__(self):
        res = _Resolver(self.uuid)
        self.addr = await _wait_for(lambda: res.addr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        return self

    async def __aexit__(self, *exc):
        self.sock.close()

    # -------- RPC --------
    async def call(self, method, params=None):
        msg = cbor2.dumps({"m":method, "p":params or {}})
        self.sock.sendto(bytes([RPC_CH])+msg, self.addr)
        data,_ = self.sock.recvfrom(2048)
        return cbor2.loads(data[1:])

    # -------- OTA --------
    async def ota(self, blob:bytes):
        size = len(blob); sha = hashlib.sha256(blob).digest()
        meta = cbor2.dumps({"cmd":"BEGIN","size":size,"sha":sha})

        def send(seq,p):
            pkt = bytes([OTA_CH])+struct.pack(">H",seq)+p
            self.sock.sendto(pkt, self.addr)

        def wait_ack(seq):
            data,_ = self.sock.recvfrom(64)
            if data[:3]!=ACK or data[3:5]!=struct.pack(">H",seq):
                raise RuntimeError("bad ACK", data)

        # begin
        send(0, meta); wait_ack(0)

        # data
        for seq,off in enumerate(range(0,size,CHUNK), start=1):
            send(seq, blob[off:off+CHUNK]); wait_ack(seq)

        # end
        send(0, cbor2.dumps({"cmd":"END"})); wait_ack(0)
