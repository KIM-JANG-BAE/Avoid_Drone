import asyncio
import websockets
import sys



async def send_file():
    try:
        async with websockets.connect('ws://your server ip:5260') as websocket:

            # Read and send the file content in chunks
            file_path = '/home/wook/mesh_gen' + arg1 + '.obj'
            #file_path = '/home/wook/Capston/mesh_gen.obj'
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(1024)  # Read the file in 1KB chunks
                    if not chunk:
                        break
                    await websocket.send(chunk)
               
                await websocket.send(b'EOF')
   
    except Exception:
        await asyncio.sleep(1)



arg1 = sys.argv[1]

asyncio.get_event_loop().run_until_complete(send_file())
