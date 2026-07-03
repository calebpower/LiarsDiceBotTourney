import sys
import requests

class APIClient:
    """
    Manages the HTTP lifecycle session with the centralized display manager API.
    Handles dynamic UDP stream acquisition and cleanup.
    """
    def __init__(self, api_url, api_key, display_ids, verify=True):
        # Normalize URL to ensure it has a base protocol scheme and no trailing slashes
        base_url = api_url if api_url.startswith("http") else f"http://{api_url}"
        self.api_url = base_url.rstrip("/")
        self.api_key = api_key
        self.display_ids = display_ids
        self.verify = verify
        self.allocated_port = None

        if not self.api_key:
            print("Error: APIClient initiated without an API_KEY.")
            sys.exit(1)

    def _get_headers(self):
        """Generates standard authorization headers required by the API."""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def open_stream(self):
        """
        Sends a POST request to request a dynamic UDP pass-thru stream
        bound to our target physical train signal display panels.
        """
        url = f"{self.api_url}/api/streams"
        payload = {"display_ids": self.display_ids}
        
        print(f"> Requesting UDP stream configuration from API for display IDs: {self.display_ids}...")
        
        try:
            # We enforce a clean 10-second request timeout to prevent hanging on boot
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10, verify=self.verify)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                print(f"API Error: Stream allocation rejected. Message: {data.get('message')}")
                sys.exit(1)
                
            port = data.get("port")
            if not port:
                print("API Error: Stream request returned success, but no dynamic port was provided.")
                sys.exit(1)
                
            self.allocated_port = int(port)
            print(f"> Stream registration accepted. Dedicated listener opened on UDP port: {self.allocated_port}")
            return self.allocated_port

        except requests.exceptions.RequestException as e:
            print(f"Network Error during stream acquisition: {e}")
            sys.exit(1)

    def close_stream(self):
        """
        Deletes the active stream assignment by its port identifier.
        Ensures the multiplexer clears the line for future applications.
        """
        if not self.allocated_port:
            return

        url = f"{self.api_url}/api/streams/{self.allocated_port}"
        print(f"\n> Releasing stream allocation on port {self.allocated_port}...")
        
        try:
            response = requests.delete(url, headers=self._get_headers(), timeout=10, verify=self.verify)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                print("> Stream allocation successfully dropped from display multiplexer.")
            else:
                print(f"Warning: API failed to drop stream cleanly: {data.get('message')}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network Error encountered during stream teardown: {e}")
        finally:
            self.allocated_port = None
