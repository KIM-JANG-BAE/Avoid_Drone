from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2

app = FastAPI()

def generate_frames():
    i = 0
    while True:
        try:
            #i = i % 100
            #image_pathi = '/home/jeonjunsu/images/image' + str(i) + '.jpg'
            image_path = '/home/jeonjunsu/images/image.jpg'
            frame = cv2.imread(image_path)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #i = i+1
        except:
            pass

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5255)
