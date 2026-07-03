#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow",
#     "requests",
#     "pyzmq",
# ]
# ///

import os
import sys
import time
import signal
import argparse

# Inject package lookup boundary to guarantee smooth relative module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from esoteric_scoreboard import EsotericScoreboardOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Launcher for the Esoteric Scoreboard Train Signal Telematics Engine.")
    parser.add_argument("api_host", help="The display manager host API endpoint (e.g., 192.168.1.50:8080)")
    parser.add_argument("zmq_address", help="The main tournament server ZMQ broadcast address (e.g., 127.0.0.1:5556)")
    parser.add_argument("--display-ids", default="1,2,3", help="Comma-separated physical display panel IDs (default: 1,2,3)")
    parser.add_argument("--fps", type=int, default=30, help="Target refresh rendering loop frame rate (default: 30)")
    parser.add_argument("-k", "--insecure", action="store_true", help="Allow insecure server connections when using SSL/TLS")
    parser.add_argument("--udp-host", help="Optional direct destination IP/host for UDP streaming if the API is behind a proxy")
    args = parser.parse_args()

    # Secure the API authentication token from the local machine environment
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("Critical Error: The API_KEY environment variable is missing.")
        print("Please export a valid key to your terminal session: $ export API_KEY='your_secret_token'")
        sys.exit(1)

    # Sanitize and compile string tokens into numerical array lookups
    try:
        display_id_list = [int(x.strip()) for x in args.display_ids.split(",")]
    except ValueError:
        print("Error: --display-ids parameter must be clean, comma-separated integers (e.g., 1,2,3).")
        sys.exit(1)

    # Instantiate the unified system controller
    orchestrator = EsotericScoreboardOrchestrator(
        api_url=args.api_host,
        api_key=api_key,
        display_ids=display_id_list,
        zmq_address=args.zmq_address,
        verify=not args.insecure,
        udp_host=args.udp_host
    )

    # Intercept system teardown boundaries to fire API de-allocations reliably
    def shutdown_handler(signum, frame):
        orchestrator.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Run the dynamic startup pipeline sequence
    try:
        orchestrator.startup()
    except Exception as e:
        print(f"Boot Failure: Scoreboard crashed during initialization: {e}")
        sys.exit(1)

    # Establish pacing bounds based on the requested target FPS limits
    frame_duration_S = 1.0 / args.fps
    print(f"> Primary ticking loop initialized. Locking frame rate to {args.fps} FPS (~{frame_duration_S:.4f}s intervals).")
    print("> Master anchor timing engine initialized in dynamic adaptive sync mode.")
    print("> Press CTRL+C to safely exit and drop display streams.")

    while True:
        start_time = time.time()
        
        try:
            # Ticks the state machine and blasts the frame payload down the UDP socket
            orchestrator.run_frame()
        except Exception as e:
            print(f"\nExecution Warning: Core engine dropped a frame cycle: {e}")

        # Compute execution cost to guarantee consistent visual timings across variable host processors
        elapsed_time = time.time() - start_time
        sleep_remainder = frame_duration_S - elapsed_time
        
        if sleep_remainder > 0:
            time.sleep(sleep_remainder)

if __name__ == "__main__":
    main()
