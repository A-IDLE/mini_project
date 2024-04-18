from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import base64

fastapi_app = FastAPI()

templates = Jinja2Templates(directory="templates")

# 메인화면


@fastapi_app.get("/")
def home(request: Request):

    return templates.TemplateResponse("index.html",
                                      {"request": request, })


@fastapi_app.post("/uploadimage")
async def upload_image(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 예시: 이미지를 회색조로 변환
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, encoded_img = cv2.imencode('.jpg', gray_img)
    encoded_img_str = base64.b64encode(encoded_img).decode('utf-8')

    return JSONResponse(content={"image": encoded_img_str})


# generate video frames
def generate_frames(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Encode frame to JPEG format
        _, encoded_frame = cv2.imencode('.jpg', gray_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_frame) + b'\r\n')

    cap.release()


@fastapi_app.post("/uploadvideo")
async def upload_video(video: UploadFile = File(...)):
    contents = await video.read()
    with open("uploaded_video.mp4", "wb") as f:
        f.write(contents)

    return StreamingResponse(generate_frames("uploaded_video.mp4"), media_type="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    uvicorn.run('main:fastapi_app',
                host='localhost', port=9000, reload=False)
