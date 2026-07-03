import threading
import json
import zmq

class ZMQListener(threading.Thread):
    """
    Background worker thread that listens to real-time tournament logs
    broadcasted by the main Liar's Dice server via ZeroMQ PUB/SUB.
    """
    def __init__(self, zmq_address, state_machine):
        super().__init__()
        self.zmq_address = zmq_address
        self.state_machine = state_machine
        
        self.name = "ZMQListenerThread"
        self.daemon = True
        self._stop_event = threading.Event()
        
        # Initialize ZeroMQ context and subscriber socket structures
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")

    def run(self):
        connection_url = self.zmq_address if self.zmq_address.startswith("tcp://") else f"tcp://{self.zmq_address}"
        print(f"> Connecting telemetry listener to server broadcast line at {connection_url}...")
        
        try:
            self.socket.connect(connection_url)
        except Exception as e:
            print(f"ZMQ Critical Error: Failed to attach socket to endpoint {connection_url}: {e}")
            return

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while not self._stop_event.is_set():
            try:
                socks = dict(poller.poll(250))
                
                if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                    multipart_msg = self.socket.recv_multipart()
                    self._process_message(multipart_msg)
                    
            except zmq.ZMQError as e:
                if not self._stop_event.is_set():
                    print(f"ZMQ Listener Warning: Intermittent socket exception: {e}")
            except Exception as e:
                print(f"ZMQ Listener Error: Unexpected exception in telemetry loop: {e}")

        self.socket.close()
        print("> ZMQ Telemetry listener thread has exited cleanly.")

    def _process_message(self, multipart_msg):
        """Dispatches unpacked network frames directly to corresponding engine handlers."""
        if len(multipart_msg) < 2:
            return

        topic = multipart_msg[0]
        payload_bytes = multipart_msg[1]

        try:
            # We filter out all GameLogs entirely now, avoiding unnecessary processing cycles
            if topic == b'TourneyLog':
                log_data = json.loads(payload_bytes.decode('utf-8'))
                self.state_machine.handle_tournament_completion(log_data)

        except json.JSONDecodeError as e:
            print(f"ZMQ Parser Warning: Abandoned malformed JSON frame on topic {topic}: {e}")
        except Exception as e:
            print(f"ZMQ Processor Error: Encountered failure parsing event data: {e}")

    def stop(self):
        """Triggers the structural flag to halt execution and unblock the polling loop."""
        print("> Signaling ZMQ telemetry listener thread to halt...")
        self._stop_event.set()
