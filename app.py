import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import csv

st.title("Analisador de Tinta Offset (Web)")

pdf_file = st.file_uploader("Selecione o PDF (1 página, 1 cor)", type="pdf")
n = st.number_input("Número de setores verticais", min_value=1, max_value=100, value=20)

if st.button("Analisar") and pdf_file:
    # converter PDF -> imagem
    images = convert_from_bytes(pdf_file.read(), first_page=1, last_page=1, dpi=200)
    img = images[0].convert("L")
    bin_img = img.point(lambda x: 0 if x < 128 else 255, '1')
    arr = np.array(bin_img)
    h, w = arr.shape
    sector_w = w // n

    percentages = []
    for i in range(n):
        sector = arr[:, i*sector_w : w if i == n-1 else (i+1)*sector_w]
        percentages.append(round((sector==0).sum()/sector.size * 100, 1))

    # desenhar
    out = bin_img.convert("RGB")
    draw = ImageDraw.Draw(out)
    font_size = int(sector_w * 0.8)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for i, pct in enumerate(percentages):
        x = i * sector_w
        draw.line([(x,0),(x,h)], fill="red", width=1)
        txt = f"{pct}%"
        bw, bh = draw.textbbox((0,0), txt, font=font)[2:]
        draw.text((x + (sector_w-bw)//2, h - bh - 5), txt, fill="blue", font=font)

    # exibir imagem
    st.image(out, caption="Resultado", use_column_width=True)

    # criar e disponibilizar PDF
    buf = io.BytesIO()
    out.save(buf, "PDF")
    st.download_button("📄 Baixar PDF", buf.getvalue(), file_name="analise.pdf", mime="application/pdf")

    # criar CSV
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(["Setor","Tinta(%)"])
    writer.writerows([[i+1, p] for i, p in enumerate(percentages)])
    st.download_button("📥 Baixar CSV", csv_buf.getvalue(), file_name="analise.csv", mime="text/csv")
