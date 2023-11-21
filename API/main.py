'''
API for pulling OpenCV and MediaPipe data
'''

#Importing FASTAPI class
from fastapi import FastAPI

#FASTAPI instance
app = FastAPI()

#Path for OpenCV data
@app.post("/OpenCV/")
async def pull_OpenCV():
    # Process data here
    pass #REMOVE
    # return response body using "return"

#Path for MediaPipe data
@app.post("/MediaPipe/")
async def pull_MediaPipe():
    # Process data here
    pass #REMOVE
    # return response body using "return"