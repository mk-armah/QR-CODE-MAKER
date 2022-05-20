from enum import Enum
from secrets import choice
from tracemalloc import StatisticDiff
from fastapi import Depends, FastAPI,Body, File, UploadFile,status,Request,Form,Query
from fastapi.staticfiles import StaticFiles
import qrcode
import io
from starlette.responses import Response,RedirectResponse
from pydantic import BaseModel
from typing import List, Optional,Union
from enum import Enum
import numpy as np

from starlette.templating import Jinja2Templates
import uvicorn
templates = Jinja2Templates(directory="templates_main")


app = FastAPI()

app.mount("/templates_main/css",StaticFiles(directory="templates_main"),name="css")
app.mount("/templates_main/assets",StaticFiles(directory= "templates_main/assets"),name = "assets")
app.mount("/templates_main/bootstrap",StaticFiles(directory="templates_main/bootstrap"),name = "bootstrap")
app.mount("/templates_main/css",StaticFiles(directory="templates_main/css"),name = "css")
app.mount("/template_main/fonts",StaticFiles(directory="templates_main/fonts"),name = "fonts")
app.mount("/template_main/img",StaticFiles(directory="templates_main/img"),name = "img")
app.mount("/templates_main/js",StaticFiles(directory= "templates_main/js"),name = "js")
app.mount("/templates_main/made_images",StaticFiles(directory="templates_main/made_images"),name = "qrcode")



# @app.post("/fastqr")
# def fastqr(text:str = Form(...)):
#     img = qrcode.make(text)
#     bytesio = io.BytesIO()
#     img.save(bytesio, "PNG")

#     return Response(bytesio.getvalue(),media_type = "image/png") 

### CUSTOM QR CODE MAKER ###





class CustomQR(qrcode.QRCode):
    def __init__(self,version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4, image_factory=None, mask_pattern=None,style = None):
        super(CustomQR,self).__init__()
        self.embed_image  = None
        self.set_image = False


qr = CustomQR()

def resource():
    return qr



@app.post("/fastqr")
def fastqr(text:str = Form(...),resource:resource = Depends(resource)):
    
    resource.add_data(text)
    img = resource.make_image()
    img.save(r"./templates_main/made_images/101.png","png")
    resource.set_image = True

    url = app.url_path_for("fastqr")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER) 



@app.get("/")
def index(request: Request,  resource: resource = Depends(resource)):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "qrcode": resource})



@app.get("/fastqr")
def fastsetup(request: Request,  resource: resource = Depends(resource)):
    return templates.TemplateResponse("fastqr.html",
                                      {"request": request, "resource": resource})


@app.get("/customqr")
def customize(request: Request,  resource: resource = Depends(resource)):
    return templates.TemplateResponse("customqr.html",
                                      {"request": request, "qrcode": resource})




@app.post("/customqr")
def customqr(request:Request,version:Optional[int] = Query(None,gt = 0,le = 40,description="Integer from 1 to 40 that controls the size of the QR Code"),
        error_correction:Optional[int] = Query(0,le = 3,ge=0,description= "controls the error correction used for the QR Code"),
        box_size:Optional[int] = Query(10,description = "controls how many pixels each “box” of the QR code is"),
        border:Optional[int] = Query(4,describtion = "controls how many boxes thick the border should be"),
        resource:Optional[resource] = Depends(resource)):

    
    resource.version =  resource.version
    resource.error_correction = error_correction
    resource.box_size = box_size
    resource.border = border
    size:tuple = (200,300)

    # url = app.url_path_for("customqr")
    # return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)




@app.post("/customqr/add_data")
async def add_data(request:Request,text:str=Body(...,description="Enter text to embed"),
resource:Optional[resource] = Depends(resource)):
    
    resource.add_data(text)

    url = app.url_path_for("customqr")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


class ImageFormat(str,Enum):
    SVG:str = 'SVG'
    PNG:str = "PNG"

@app.post("/image_format")
def image_format(format:Optional[ImageFormat]):
    pass




@app.get("/customqr/get_qr")
async def get_qrcode(request:Request,fill_color:Optional[str] = "black",back_color:Optional[str] = "white",
resource:Optional[resource] = Depends(resource)):

    # resource.add_data(resource.text)
    resource.make(fit=True)
    qrcode_image = resource.make_image(fill_color="black", back_color="white")
    bytesio = io.BytesIO()
    qrcode_image.save(bytesio, "PNG")

    return Response(bytesio.getvalue(),media_type = "image/png")



@app.delete("/delete_entry")
async def clear(request:Request,resource:resource = Depends(resource)):
    
    resource.clear()

    url = app.url_path_for("customqr")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

