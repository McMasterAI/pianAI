'''
API for pulling OpenCV and MediaPipe data
'''

#Importing FASTAPI class
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2

#FASTAPI instance
app = FastAPI()

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')
        
# For live video stream
@app.get("/")
async def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # return StreamingResponse(generate())
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/uploadAudio/")
async def load_Audio(file:UploadFile):
    #Process file data by referencing "file"
    #Use "file.file" to reference file as a file-like object
    #return response body using "return"
    return file.filename

@app.post("/Midi/")
async def load_Midi(file:UploadFile):
    #Process file data by referencing "file"
    # User "file.file" to reference file as a file-like object
    pass



# #Path for OpenCV data
# @app.post("/OpenCV/")
# async def pull_OpenCV():
#     # Process data here
#     pass #REMOVE
#     # return response body using "return"


# #Path for MediaPipe data
# @app.post("/MediaPipe/")
# async def pull_MediaPipe():
#     # Process data here
#     pass #REMOVE
#     # return response body using "return"