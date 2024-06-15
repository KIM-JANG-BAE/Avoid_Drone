import asyncio
import websockets

process_queue = asyncio.Queue(maxsize=5)

async def receive_data(websocket, path):
    print('streamer connected')
    while True:
        try:
            data = await websocket.recv()
            print(data)
            if process_queue.full():
                await process_queue.get()
            await process_queue.put(data)
        except websockets.exceptions.ConnectionClosedError:
            print("streamer disconnected")
            break

async def send_data(websocket, path):
    print('listener connected')
    while True:
        try:
            data = await process_queue.get()
            await websocket.send(data)
        except websockets.exceptions.ConnectionClosedError:
            print("listener disconnected")
            break

async def main(websocket, path):
    part = await websocket.recv()
    if part == 'streamer':
        await receive_data(websocket, path)
    elif part == 'listener':
        await send_data(websocket, path)
    else:
        print("Unknown client type:", part)

if __name__ == "__main__":
    start_server = websockets.serve(main, 'your server IP', your port number)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

