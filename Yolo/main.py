from modelroblox import get_yolov5_roblox
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from io import BytesIO
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

app = FastAPI(title="Logo Detection API",
              description="""Upload logo image and the API will respond with merchant name""",
              version="0.0.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can specify specific origins if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load model with confidence value
model_logo = get_yolov5_roblox(0.9)


def convert_names_to_numbers(names, xmins):
    # แปลงชื่อเป็นตัวเลข
    name_to_number = {
        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9'
    }

    # ค่าที่ใช้เป็นเกณฑ์ในการเว้นวรรค
    threshold = 35  # คุณสามารถปรับเปลี่ยนเกณฑ์นี้ได้ตามต้องการ

    # สร้างรายการสำหรับเก็บตัวเลขที่มีการเว้นวรรค
    formatted_numbers = []

    # วนลูปเพื่อแปลงชื่อเป็นตัวเลข
    for i, name in enumerate(names):
        number = name_to_number.get(name, '')  # แปลงชื่อเป็นตัวเลข
        if i == 0:
            formatted_numbers.append(number)  # เพิ่มค่าตัวแรก
        else:
            # ตรวจสอบความแตกต่างของ xmin
            diff = xmins[i] - xmins[i - 1]
            if diff > threshold:  # ถ้าความแตกต่างมากกว่าเกณฑ์
                formatted_numbers.append(' ')  # เพิ่มเว้นวรรค
            formatted_numbers.append(number)  # เพิ่มตัวเลข

    # รวมตัวเลขที่จัดรูปแบบ
    return ''.join(formatted_numbers)


data = []

@app.post("/detectImage")
async def detect_image(file: UploadFile):
    global data

    img = Image.open(BytesIO(await file.read()))

    results = model_logo(img, size=640)
    results.render()

    label_result = results.pandas().xyxy[0]

    print(label_result)

    # เรียงข้อมูลตาม xmin
    sorted_label_result = label_result.sort_values(by='xmin').reset_index(drop=True)

    # # แสดงผลลัพธ์ที่เรียงแล้ว
    # print("Sorted Label Result:")
    print(sorted_label_result)

    # ดึงค่า name ทั้งหมดใน sorted_label_result
    names = sorted_label_result['name'].tolist()
    xmins = sorted_label_result['xmin'].tolist()

    # แสดงผลลัพธ์
    print("Names:")
    print(names)

    # แปลงชื่อเป็นตัวเลขและจัดรูปแบบ
    result = convert_names_to_numbers(names, xmins)

    print("Result:")
    print(result)

    # data = {"gem":result.split(" ")[0],"gold":result.split(" ")[1]}

    data.append({"gem":result.split(" ")[0],"gold":result.split(" ")[1]})

    # Save the rendered image as JPEG
    bytes_io = BytesIO()
    img_base64 = Image.fromarray(results.ims[0])  # Corrected the attribute from 'imgs' to 'ims'
    img_base64.save(bytes_io, format="jpeg")
    
    return Response(bytes_io.getvalue(), media_type="image/jpeg")

@app.post("/addlog")
async def addlog():
    print("")

@app.get("/getlog")
async def getlog():
    total_gem = 0
    total_gold = 0
    for entry in data:
        total_gem += int(entry['gem'])
        total_gold += int(entry['gold'])
    print(data)
    return {
        "data": data,          # Use a string key for the data
        "total_gem": total_gem, # Use string keys for totals
        "total_gold": total_gold
    }
