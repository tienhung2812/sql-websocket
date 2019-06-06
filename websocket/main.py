import websocket
import setting

args = vars(setting.ap.parse_args())
ws = websocket.Websocket(args['host'],args['port'])
ws.start()