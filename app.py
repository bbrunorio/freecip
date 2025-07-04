import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import csv
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

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
            percentages.append(round((black / total) * 100, 1))

        # Desenhar imagem com linhas e porcentagens
        out = bin_img.convert("RGB")
        draw = ImageDraw.Draw(out)

        # Fonte com tamanho fixo grande
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font_size = 60
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        for i, pct in enumerate(percentages):
            x = i * sector_w
            draw.line([(x, 0), (x, h)], fill="red", width=1)
            text = f"{pct}%"
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except:
                text_w, text_h = draw.textsize(text, font=font)
            draw.text((x + (sector_w - text_w) // 2, h - text_h - 10), text, fill="blue", font=font)

        # Exibir imagem processada
        st.image(out, caption="Resultado com setores e porcentagens", use_container_width=True)

        # Salvar imagem em buffer PNG
        img_buf = io.BytesIO()
        out.save(img_buf, format="PNG")
        img_buf.seek(0)

        # Gerar PDF com ReportLab
        pdf_buf = io.BytesIO()
        c = canvas.Canvas(pdf_buf, pagesize=A4)
        page_width, page_height = A4
        img_reader = ImageReader(img_buf)
        c.drawImage(img_reader, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True)
        c.showPage()
        c.save()
        pdf_buf.seek(0)

        # Botão de download do PDF
        st.download_button(
            "📥 Baixar resultado em PDF",
            pdf_buf.read(),
            file_name="analise_tinteiro.pdf",
            mime="application/pdf"
        )

        # Gerar CSV com os dados
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["Setor", "Preenchimento Preto (%)"])
        writer.writerows([[i + 1, pct] for i, pct in enumerate(percentages)])
        st.download_button("📊 Baixar CSV com dados", csv_buf.getvalue(), file_name="analise_tinteiro.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
