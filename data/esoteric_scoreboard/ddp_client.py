import socket

class DDPClient:
    """
    Handles the low-overhead UDP data transmission pipeline.
    Responsible for encapsulating raw grayscale matrix frame payloads
    with standard DDP framing protocols.
    """
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
        
        # Standard 10-byte DDP Header configured for a 300-byte payload:
        # 0x41: Flags (v1, Push)
        # 0x00, 0x00: Sequence numbers (disabled/unmanaged)
        # 0x01: Data type (Grayscale/Luminance payload)
        # 0x00: Destination ID
        # 0x00, 0x00, 0x00, 0x00: Offset bytes
        # 0x01, 0x2C: Length of payload (300 bytes in big-endian hex)
        self.ddp_header = bytearray([0x41, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x2C])
        
        # Open a standard IPv4 UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"> Network socket opened. Blasting raw frames to {self.target_ip}:{self.target_port} via UDP.")

    def send_frame(self, payload):
        """
        Appends the protocol tracking header onto the incoming 300-byte list/bytearray
        and transmits it immediately down the socket.
        """
        if not isinstance(payload, (bytes, bytearray)):
            payload = bytearray(payload)

        # Validate layout bounds to prevent hardware glitching
        if len(payload) != 300:
            print(f"Warning: Discarding corrupted frame. Payload size must be exactly 300 bytes, got {len(payload)}.")
            return

        try:
            packet = self.ddp_header + payload
            self.sock.sendto(packet, (self.target_ip, self.target_port))
        except Exception as e:
            print(f"Network Socket Error during DDP transmission: {e}")

    def close(self):
        """Cleanly releases the system socket handle."""
        if self.sock:
            try:
                self.sock.close()
                print("> DDP UDP transmission pipe closed.")
            except Exception:
                pass
            finally:
                self.sock = None
