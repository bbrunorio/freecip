import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import csv
import fitz  # PyMuPDF

st.set_page_config(page_title="Analisador de Tinteiro Offset", layout="wide")
st.title("🖨️ Analisador de Tinteiro Offset")

pdf_file = st.file_uploader("📄 Selecione um PDF com 1 página e 1 cor (preto)", type="pdf")
n = st.number_input("🔢 Número de setores verticais", min_value=1, max_value=100, value=20)

if st.button("Analisar") and pdf_file:
    try:
        # Lê o PDF e extrai a primeira página como imagem (RGB)
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
        bin_img = img.point(lambda x: 0 if x < 128 else 255, '1')
        arr = np.array(bin_img)
        h, w = arr.shape
        sector_w = w // n

        percentages = []
        for i in range(n):
            sector = arr[:, i * sector_w : w if i == n - 1 else (i + 1) * sector_w]
            black = np.sum(sector == 0)
            total = sector.size
            percentages.append(round((black / to
