import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import fitz  # PyMuPDF
import zipfile

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
        soma = np.sum(setor)
        total = setor.size * 255
        porcentagem = round(100 - (soma / total) * 100, 1)
        porcentagens.append(porcentagem)
    return porcentagens

def desenhar_imagem(base_img, porcentagens, cor_nome="Preto"):
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

    # Nome da cor no topo (5% da altura)
    try:
        bbox = draw.textbbox((0, 0), cor_nome, font=font)
        _, _, tw, th = bbox
    except:
        tw, th = draw.textsize(cor_nome, font=font)
    y_nome_cor = int(h * 0.05)
    draw.text((10, y_nome_cor), cor_nome, fill="black", font=font)

    # Porcentagens nos setores
    for i, pct in enumerate(porcentagens):
        x = i * sector_w
        draw.line([(x, 0), (x, h)], fill="red", width=1)
        texto = f"{pct}%"
        try:
            bbox = draw.textbbox((0, 0), texto, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except:
            tw, th = draw.textsize(texto, font=font)
        y_text = int(h * 0.95 - th)
        draw.text((x + (sector_w - tw) // 2, y_text), texto, fill="blue", font=font)

    return img_color

if pdf_file and st.button("Analisar"):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)

    if mode == "Preto (K)":
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
        porcentagens = calcular_setores(img, n)
        resultado = desenhar_imagem(img, porcentagens, cor_nome="Preto")
        st.image(resultado, caption="Canal Preto (K)", use_container_width=True)

        img_buf = io.BytesIO()
        resultado.save(img_buf, format="PNG")
        img_buf.seek(0)
        st.download_button("🖼️ Baixar PNG do Preto", img_buf, file_name="preto_k.png", mime="image/png")

    else:
        pix = page.get_pixmap(dpi=200, colorspace=fitz.csCMYK)
        img = Image.frombytes("CMYK", [pix.width, pix.height], pix.samples)
        canais = img.split()
        nomes = ["Ciano", "Magenta", "Amarelo", "Preto"]
        arquivos = []

        for nome, canal in zip(nomes, canais):
            inverso = Image.eval(canal, lambda x: 255 - x)
            porcentagens = calcular_setores(inverso, n)
            resultado = desenhar_imagem(inverso, porcentagens, cor_nome=nome)
            st.image(resultado, caption=f"Canal {nome}", use_container_width=True)

            buf = io.BytesIO()
            resultado.save(buf, format="PNG")
            buf.seek(0)
            arquivos.append((f"{nome.lower()}.png", buf.read()))

        # Empacotar tudo em um .zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for nome_arquivo, conteudo in arquivos:
                zip_file.writestr(nome_arquivo, conteudo)
        zip_buffer.seek(0)
        st.download_button("📦 Baixar todas as imagens CMYK (.zip)", zip_buffer, file_name="analise_cmyk.zip", mime="application/zip")
