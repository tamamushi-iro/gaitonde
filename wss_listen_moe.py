import json, asyncio, websockets, logging

logging.basicConfig(filename='.errors/wss_error.log', level=logging.WARNING, format='[%(asctime)s] %(levelname)-8s %(name)-12s {%(message)s}')
logger = logging.getLogger('wss_listen.moe.py')

logger.warning('Program Restarted...')

async def send_ws(ws, data):
	json_data = json.dumps(data)
	await ws.send(json_data)

async def _send_pings(ws, interval=45):
	while True:
		await asyncio.sleep(interval)
		msg = { 'op': 9 }
		await send_ws(ws, msg)

async def main(loop):
	ws = await websockets.connect('wss://listen.moe/gateway_v2')
	while True:
		data = json.loads(await ws.recv())
		if data['op'] == 0:
			heartbeat = data['d']['heartbeat'] / 1000
			loop.create_task(_send_pings(ws, heartbeat))
		elif data['op'] == 1:
			with open('nowPlaying.json', 'w') as file:
				json.dump(data, file)

if __name__ == '__main__':
	try:
		loop = asyncio.get_event_loop()
		loop.run_until_complete(main(loop))
	except Exception as e:
		logger.error(e)
