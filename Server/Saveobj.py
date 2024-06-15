import asyncio
import websockets

async def file_receiver(websocket):
    print("Client connected")


    # Save the file
    with open('/home/jeonjunsu/obj/mesh1.obj', 'wb') as f:
        while True:
            try:
                file_content = await websocket.recv()
                if file_content == b'EOF':
                    break
                f.write(file_content)
            except websocket.exceptions.ConnectionClosed:
                pass

    print(f"File received and saved")

start_server = websockets.serve(file_receiver, 'your server ip', your port number)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
