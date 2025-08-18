import asyncio
from typing import Dict


class MetricStorage:
    """In-memory store: key -> { timestamp: value }"""
    def __init__(self):
        self._store: Dict[str, Dict[int, float]] = {}

    def put(self, key: str, value: float, timestamp: int) -> None:
        if key not in self._store:
            self._store[key] = {}
        # overwrite if timestamp exists, otherwise create
        self._store[key][timestamp] = value

    def get(self, key: str) -> Dict[str, Dict[int, float]]:
        # return a shallow copy of the requested data structure
        if key == "*":
            return {k: dict(v) for k, v in self._store.items()}
        if key in self._store:
            return {key: dict(self._store[key])}
        return {}


class CommandError(Exception):
    """Raised on bad commands or parameters"""
    pass


class CommandHandler:
    """Parses and executes text commands against MetricStorage"""
    def __init__(self, storage: MetricStorage):
        self.storage = storage

    def handle(self, line: str) -> Dict[str, Dict[int, float]]:
        """
        Accepts a single command line without trailing newline.
        For 'put' returns empty dict (no body on success),
        for 'get' returns a dict with requested metrics.
        Raises CommandError on malformed request.
        """
        parts = line.split()
        if not parts:
            raise CommandError

        cmd = parts[0]

        if cmd == "put":
            # expected: put <key> <value> <timestamp>
            if len(parts) != 4:
                raise CommandError
            key = parts[1]
            try:
                value = float(parts[2])
                timestamp = int(parts[3])
            except (ValueError, TypeError):
                raise CommandError
            self.storage.put(key, value, timestamp)
            return {}  # indicate successful put with no payload

        elif cmd == "get":
            # expected: get <key>
            if len(parts) != 2:
                raise CommandError
            key = parts[1]
            return self.storage.get(key)

        else:
            raise CommandError


class MetricsProtocol(asyncio.Protocol):
    """
    Asyncio protocol for the metrics server.
    The server buffers bytes until a newline-terminated request arrives,
    then processes it as a single command line (multiple lines in one packet
    are rejected as malformed).
    """
    OK = "ok"
    ERR = "error"
    ERR_TEXT = "wrong command"
    TERM = "\n"

    storage = MetricStorage()  # shared across all connections

    def __init__(self):
        self.transport = None
        self._buffer = b""
        self._handler = CommandHandler(self.storage)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data: bytes):
        # accumulate bytes
        self._buffer += data

        # only process when we received a terminating newline
        try:
            text = self._buffer.decode()
        except UnicodeDecodeError:
            self._send_error()
            self._buffer = b""
            return

        if not text.endswith(self.TERM):
            # wait for more data
            return

        # strip only the final newline(s) and make sure there's exactly one command line
        # if multiple lines are present, treat it as wrong command
        lines = [ln for ln in text.split(self.TERM) if ln != ""]
        # reset buffer for next request(s)
        self._buffer = b""

        if len(lines) != 1:
            # the protocol expects a single command per request
            self._send_error()
            return

        request_line = lines[0]

        try:
            result = self._handler.handle(request_line)
            # successful handling -> build ok response
            body = self._build_body(result)
            response = f"{self.OK}\n{body}\n"
            self.transport.write(response.encode())
        except CommandError:
            self._send_error()

    def _build_body(self, data: Dict[str, Dict[int, float]]) -> str:
        """
        Build body lines from storage dict:
        For each key (sorted by insertion order of dict, but we explicitly sort keys),
        list lines 'key value timestamp' sorted by timestamp ascending.
        If data is empty, return an empty string (so final response is 'ok\n\n').
        """
        lines = []
        for key in sorted(data.keys()):
            timestamp_map = data[key]
            for timestamp in sorted(timestamp_map.keys()):
                value = timestamp_map[timestamp]
                lines.append(f"{key} {value} {timestamp}")
        if lines:
            return "\n".join(lines) + "\n"  # ensure trailing newline before final blank line
        return ""

    def _send_error(self):
        resp = f"{self.ERR}\n{self.ERR_TEXT}\n\n"
        self.transport.write(resp.encode())


def run_server(host: str, port: int):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(MetricsProtocol, host, port)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)
