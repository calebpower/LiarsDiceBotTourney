"""
Esoteric Scoreboard Package
Manages real-time visual telematics for a 30x10 RYB horizontal train signal.
"""

from .api_client import APIClient
from .ddp_client import DDPClient
from .zmq_listener import ZMQListener
from .renderer import ScoreboardRenderer
from .state_machine import ScoreboardStateMachine

class EsotericScoreboardOrchestrator:
    """
    The master controller that ties the API handshake, network pipes,
    ZMQ data streams, and state machine together.
    """
    def __init__(self, api_url, api_key, display_ids, zmq_address, verify=True, udp_host=None):
        self.api_url = api_url
        self.api_key = api_key
        self.display_ids = display_ids
        self.zmq_address = zmq_address
        self.verify = verify
        self.udp_host = udp_host
        
        # Core subsystems
        self.api_client = None
        self.ddp_client = None
        self.zmq_listener = None
        self.renderer = None
        self.state_machine = None
        self.is_running = False

    def startup(self):
        """Executes the sequential boot and handshake pipeline."""
        print("> Booting Esoteric Scoreboard Subsystems...")
        
        # 1. Initialize the graphics and state machine
        self.renderer = ScoreboardRenderer()
        self.state_machine = ScoreboardStateMachine(self.renderer)
        
        # 2. Request the dynamic streaming port from the display manager API
        self.api_client = APIClient(self.api_url, self.api_key, self.display_ids, verify=self.verify)
        udp_port = self.api_client.open_stream()
        
        # 3. Open the native UDP socket targeted at that dynamic port
        target_ip = self.udp_host if self.udp_host else self.api_url.split("//")[-1].split(":")[0]
        self.ddp_client = DDPClient(target_ip, udp_port)
        
        # 4. Spin up the background ZeroMQ telemetry listener thread
        self.zmq_listener = ZMQListener(self.zmq_address, self.state_machine)
        self.zmq_listener.start()
        
        self.is_running = True
        print("> Esoteric Scoreboard is fully operational and streaming.")

    def run_frame(self):
        """Executes a single frame iteration inside the primary execution loop."""
        if not self.is_running:
            return
            
        # Update the state machine strategies and render the current 30x10 matrix
        payload = self.state_machine.update()
        
        # Blast the raw 300-byte frame down the UDP pipe
        self.ddp_client.send_frame(payload)

    def shutdown(self):
        """Guarantees a clean system teardown, avoiding loose ports on the API."""
        print("\n> Intercepted shutdown signal. Cleaning up...")
        self.is_running = False
        
        if self.zmq_listener:
            self.zmq_listener.stop()
            
        if self.ddp_client:
            self.ddp_client.close()
            
        if self.api_client:
            self.api_client.close_stream()
            
        print("> Teardown complete. Light display released safely.")
