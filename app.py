import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import io
import fitz  # PyMuPDF

st.set_page_config(page_title="Analisador de Tinteiro CMYK", layout="wide")
st.title("🖨️ Analisador de Tinteiro - Offset Manual")

pdf_file = st.file_uploader("📄 Selecione um PDF (1 página)", type="pdf")
mode = st.radio("Modo de análise", ["Preto (K)", "Colorido (CMYK)"])
n = st.number_input("🔢 Número de setores verticais", min_value=1, max_value=100, value=20)

def calcular_setores(image, num_setores):
    arr = np.array(image)
    h, w = arr.shape
    sector_w = w // num_setores
    porcentagens = []
    for i in range(num_setores):
        start = i * sector_w
        end = w if i == num_setores - 1 else (i + 1) * sector_w
        setor = arr[:, start:end]
        preto = np.sum(255 - setor)
        total = setor.size * 255
        porcentagem = round((preto / total) * 100, 1)
        porcentagens.append(porcentagem)
    return porcentagens

def desenhar_imagem(base_img, porcentagens):
    arr = np.array(base_img)
    h, w = arr.shape
    num_setores = len(porcentagens)
    sector_w = w // num_setores
    img_color = base_img.convert("RGB")
    draw = ImageDraw.Draw(img_color)

    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()

    for i, pct in enumerate(porcentagens):
        x = i * sector_w
        draw.line([(x, 0), (x, h)], fill="red", width=1)
        texto = f"{pct}%"
        try:
            bbox = draw.textbbox((0, 0), texto, font=font)
            tw, th = bbox[2] - bb
