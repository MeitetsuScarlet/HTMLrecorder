import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()
if not os.path.exists("./ogg"):
    os.makedirs("./ogg")

# CORS-block avoiding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "Welcome to my World. This is HTMLrecorder"}


@app.post("/upload/{courpus}")
async def fileget(request: Request, courpus):
    form = await request.form()

    filename = {courpus}
    filename = str(list(filename)[0]) + ".ogg"  # ONLY filename pickup
    num = 1
    uploadedpath = "./ogg"
    files = os.listdir(uploadedpath)
    while filename in files:  # avoiding @overwrite
        filename = filename.rstrip(".ogg")
        number = "(" + str(num-1) + ")"
        filename = filename.rstrip(number)
        filename = filename + "(" + str(num) + ").ogg"
        num = num + 1

    for formdata in form:  # chunk & file writing
        uploadfile = form[formdata]
        path = os.path.join("./ogg", filename)
        fout = open(path, 'wb')
        while 1:
            chunk = await uploadfile.read(100000)
            if not chunk:
                break
            fout.write(chunk)
        fout.close()
    return {"status": "OK"}  # I hope return "200"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
