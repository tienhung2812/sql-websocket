import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", type=int, default=6789,
	help="Port for Websocket")
ap.add_argument("--host", type=str, default='localhost',
	help="Host for Websocket")