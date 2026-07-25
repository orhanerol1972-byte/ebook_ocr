import streamlit as st
import fitz  # PyMuPDF
import os
import json
from google.cloud import vision
from google.oauth2 import service_account

# Sayfa tasarımı
st.set_page_config(page_title="Türkçe Kitap OCR", page_icon="📖")
st.title("📖 Türkçe Kitap OCR")
st.markdown("Google Vision API ile PDF kitaplarınızı kopyalanabilir metne dönüştürün.")

# Sol Panel: JSON Anahtarı
st.sidebar.header("🔑 Kimlik Doğrulama")
uploaded_json = st.sidebar.file_uploader("Google Cloud JSON anahtar dosyanızı yükleyin", type=['json'])

# Ana Panel: PDF Yükleme
st.header("📤 Kitabınızı Yükleyin")
uploaded_pdf = st.file_uploader("PDF kitap dosyanızı seçin", type=['pdf'])

# OCR İşlemi
if uploaded_json is not None and uploaded_pdf is not None:
    if st.button("🚀 OCR İşlemini Başlat"):
        try:
            with st.spinner("Anahtar dosyası doğrulana kadar bekleyin..."):
                service_account_info = json.load(uploaded_json)
                credentials = service_account.Credentials.from_service_account_info(service_account_info)
                client = vision.ImageAnnotatorClient(credentials=credentials)

            with st.spinner("PDF hazırlanıyor..."):
                pdf_bytes = uploaded_pdf.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                total_pages = len(doc)
                full_text = ""

            st.info(f"Kitap {total_pages} sayfa. Okuma başladı...")
            progress_bar = st.progress(0)

            for i in range(total_pages):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                
                image = vision.Image(content=img_bytes)
                response = client.document_text_detection(image=image)
                
                text = response.full_text_annotation.text
                full_text += f"\n\n--- SAYFA {i + 1} ---\n\n" + text
                progress_bar.progress((i + 1) / total_pages)

            st.success("🎉 İşlem başarıyla tamamlandı!")
            st.subheader("📝 Okunan Metin")
            st.text_area("Metin Önizleme", full_text, height=300)
            
            output_filename = uploaded_pdf.name.replace(".pdf", "_metin.txt")
            st.download_button(
                label="📥 Tüm Metni .txt Olarak İndir",
                data=full_text.encode('utf-8'),
                file_name=output_filename,
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"⚠️ Bir hata oluştu: {str(e)}")

elif uploaded_json is None:
    st.warning("👈 Lütfen sol panelden Google Cloud JSON anahtar dosyanızı yükleyin.")
elif uploaded_pdf is None:
    st.info("👆 Lütfen PDF kitabınızı yükleyin.")
  
