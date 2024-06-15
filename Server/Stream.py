
import cv2
import pickle
import queue
import websockets
import asyncio
#import predict

base_url = "your storage file path"

process_queue = asyncio.Queue(maxsize=10)

async def receive_data(websocket, Predict):
    print('streamer connected')
    i = 0
    while True:
        try:
            frame_size_bytes = await websocket.recv()
            frame_size = int.from_bytes(frame_size_bytes, byteorder='big')
            if frame_size == 0:
                continue
            frame_data = b''
            while len(frame_data) < frame_size:
                packet = await websocket.recv()
                if not packet:
                    break
                frame_data += packet

            frame = pickle.loads(frame_data)

            print('put', process_queue.qsize())

            if process_queue.full():
                await process_queue.get()


            image_path = "/home/jeonjunsu/images/image.jpg"
            with open(image_path, 'wb') as f:
                f.write(frame)

            #frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            #frame = Predict.pred(frame)

            #frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5, interpolation=c>
            #_, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_>

            '''
            if i % 2 == 1:
                #image_path = "/home/jeonjunsu/images/image"  + str(i) + '.jpg'
                image_path = "/home/jeonjunsu/images/image.jpg"
                with open(image_path, 'wb') as f:
'''

            '''
            else:
                image_path = "/home/jeonjunsu/images_3d/image.jpg"
                with open(image_path, 'wb') as f:
                    f.write(frame)
            '''
            #image_url = f"https://203.255.57.136:5254/images/image"  + str(i)>
            #await websocket.send(image_url)
            i = i + 1
            await process_queue.put(frame)



        except websockets.exceptions.ConnectionClosedError:
            print("streamer disconnected")
            break

async def send_data(websocket, Predict):
    print('Listener connected')
    i = 0
    while True:
        try:
            frame = await process_queue.get()
            print('Queue size:', process_queue.qsize())



        except websockets.exceptions.ConnectionClosedError:
            print("Listener disconnected")
            break
        except Exception as e:
            print("Error:", e)
            break

async def main(websocket):
    Predict = 0
    #Predict=predict.yolo()
    part = await websocket.recv()
    if part == 'streamer':
        await receive_data(websocket, Predict)
    elif part == 'listener':
        pass
        #await send_data(websocket,Predict)
    else:
        print("Unknown client type:", part)
if __name__ == "__main__":
    start_server = websockets.serve(main, 'your server ip', your port number)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
