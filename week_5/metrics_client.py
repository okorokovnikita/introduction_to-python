import socket
import time


class ClientError(Exception):
    """Custom exception for client errors"""
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._socket = None
        self._connect()

    def _connect(self):
        """Establish socket connection"""
        try:
            self._socket = socket.create_connection(
                (self._host, self._port), self._timeout
            )
        except socket.error as exc:
            raise ClientError(f"Connection error: {exc}")

    def _send(self, command):
        """Send command to server"""
        try:
            self._socket.sendall(command.encode())
        except socket.error as exc:
            raise ClientError(f"Send error: {exc}")

    def _receive(self):
        """Receive complete response from server"""
        buffer = b""
        while not buffer.endswith(b"\n\n"):
            try:
                chunk = self._socket.recv(4096)
                if not chunk:
                    break
                buffer += chunk
            except socket.error as exc:
                raise ClientError(f"Receive error: {exc}")
        return buffer.decode().strip()

    def put(self, metric, value, timestamp=None):
        """Store metric data"""
        ts = timestamp or int(time.time())
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ClientError(f"Invalid value: {exc}")

        command = f"put {metric} {value} {ts}\n"
        self._send(command)
        response = self._receive()
        
        if response != "ok":
            raise ClientError(f"Server rejected command: {response}")

    def get(self, metric):
        """Retrieve metric data"""
        command = f"get {metric}\n"
        self._send(command)
        response = self._receive()
        
        if not response.startswith("ok"):
            raise ClientError(f"Server error: {response}")
            
        data = {}
        # Skip status line and process remaining lines
        lines = response.split('\n')[1:]
        for line in lines:
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                continue  # Skip malformed lines
            
            key, val_str, ts_str = parts
            try:
                value = float(val_str)
                timestamp = int(ts_str)
            except (TypeError, ValueError):
                continue  # Skip invalid data
            
            if key not in data:
                data[key] = []
            data[key].append((timestamp, value))
        
        # Sort each metric's data by timestamp
        for key in data:
            data[key].sort(key=lambda x: x[0])
            
        return data

    def close(self):
        """Close socket connection"""
        try:
            if self._socket:
                self._socket.close()
        except socket.error as exc:
            raise ClientError(f"Close error: {exc}")
        finally:
            self._socket = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit"""
        self.close()
