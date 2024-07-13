import cv2
import easyocr
import base64
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Tuple
from matplotlib import pyplot as plt
from matplotlib.text import Text
from PIL import Image
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, adjust as needed
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
# Function to translate a single character to Braille Unicode
def char_to_braille(char):
    braille_offset = 0x2800  # Braille Unicode offset

    if char.isupper():
        return chr(ord(char.lower()) - ord('a') + braille_offset)  # Capital letters
    elif char.islower():
        return chr(ord(char) - ord('a') + braille_offset)  # Small letters
    elif char.isdigit():
        return chr(ord(char) - ord('0') + 0x2830)  # Numbers
    elif char == ' ':
        return '⠀'  # Braille space
    elif char == '.':
        return '⠲'  # Braille full stop
    elif char == ',':
        return '⠂'  # Braille comma
    elif char == ';':
        return '⠆'  # Braille semicolon
    elif char == ':':
        return '⠒'  # Braille colon
    elif char == '!':
        return '⠖'  # Braille exclamation mark
    elif char == '?':
        return '⠢'  # Braille question mark
    elif char == '"':
        return '⠦'  # Braille quotation mark
    elif char == '\'':
        return '⠄'  # Braille apostrophe
    elif char == '(':
        return '⠐'  # Braille left parenthesis
    elif char == ')':
        return '⠒'  # Braille right parenthesis
    elif char == '[':
        return '⠤'  # Braille left square bracket
    elif char == ']':
        return '⠦'  # Braille right square bracket
    elif char == '{':
        return '⠴'  # Braille left curly brace
    elif char == '}':
        return '⠾'  # Braille right curly brace
    elif char == '<':
        return '⠣'  # Braille less than
    elif char == '>':
        return '⠤'  # Braille greater than
    elif char == '@':
        return '⠈'  # Braille at symbol
    elif char == '#':
        return '⠼'  # Braille number sign
    elif char == '$':
        return '⠾'  # Braille dollar sign
    elif char == '%':
        return '⠨'  # Braille percent sign
    elif char == '^':
        return '⠐'  # Braille caret
    elif char == '&':
        return '⠬'  # Braille ampersand
    elif char == '*':
        return '⠔'  # Braille asterisk
    elif char == '_':
        return '⠰'  # Braille underscore
    elif char == '-':
        return '⠤'  # Braille hyphen-minus
    elif char == '+':
        return '⠖'  # Braille plus sign
    elif char == '=':
        return '⠶'  # Braille equals sign
    elif char == '/':
        return '⠌'  # Braille slash
    elif char == '\\':
        return '⠦'  # Braille backslash
    elif char == '|':
        return '⠳'  # Braille vertical bar
    elif char == '`':
        return '⠄'  # Braille grave accent
    elif char == '~':
        return '⠰'  # Braille tilde
    elif char == '§':
        return '⠴'  # Braille section sign
    elif char == '©':
        return '⠉'  # Braille copyright sign
    elif char == '®':
        return '⠗'  # Braille registered sign
    elif char == '™':
        return '⠞'  # Braille trademark sign
    elif char == '•':
        return '⠪'  # Braille bullet point
    elif char == '†':
        return '⠱'  # Braille dagger
    elif char == '‡':
        return '⠳'  # Braille double dagger
    elif char == '¶':
        return '⠒'  # Braille pilcrow sign
    elif char == '°':
        return '⠘'  # Braille degree sign
    elif char == '€':
        return '⠅'  # Braille Euro sign
    elif char == '£':
        return '⠪'  # Braille pound sign
    elif char == '¥':
        return '⠫'  # Braille yen sign
    # Add more symbols as needed
    else:
        return char  # Return the character as is for non-mapped characters

# Function to convert text to Braille
def text_to_braille(text):
    return ''.join(char_to_braille(char) for char in text)

def process_image_and_ocr(image_data):
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Error loading the image. Please check the file path.")
    
    reader = easyocr.Reader(['en'], gpu=False)
    text_detections = reader.readtext(img)
    
    braille_texts = []
    for bbox, text, score in text_detections:
        braille_texts.append(text_to_braille(text))
    
    braille_output = '\n'.join(braille_texts)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor('white')
    
    ax.text(0.5, 0.5, braille_output, ha='center', va='center', fontsize=24, fontfamily="Doulos SIL", color='black')
    
    plt.axis('off')
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    
    return img_buf, braille_output

@app.post("/upload_image_with_braille")
async def upload_image_with_braille(file: UploadFile = File(...)):
    image_data = await file.read()
    image_data = np.frombuffer(image_data, np.uint8)
    img_buf, braille_text = process_image_and_ocr(image_data)
    
    img = Image.open(img_buf)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return JSONResponse(content={"image": img_str, "braille_text": braille_text})
