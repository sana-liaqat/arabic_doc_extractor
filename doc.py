import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import fitz

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "OfficeFlow-Ai-01-01.png")

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except KeyError:
    API_KEY = None
    client = None
    st.error("API_KEY not found in secrets.toml. Please set it up.")


def extract_info_with_gemini(image):
    if not client:
        return None

    prompt = """
    You are an expert legal document analyst specializing in Arabic legal documents.
    Analyze the provided image carefully and extract the following information.
    Provide the output strictly in JSON format without any markdown formatting like ```json.

    Required JSON structure:
    {
      "id_ar": "The document ID in Arabic numerals (e.g., ١٦٧٧)",
      "id_en": "The document ID in English numerals (e.g., 1677)",
      "date_ar": "The full date in Arabic (e.g., ١٩ / ٥ / ١٤٤٢ هـ)",
      "date_en": "The full date in English (e.g., 19/05/1442 AH)",
      "subject_ar": "The complete subject line in Arabic, translated word-for-word from the document",
      "subject_en": "A precise English translation of the subject line",
      "summary_ar": "A DETAILED summary in Arabic (6-8 sentences minimum). Include: the purpose of the document, the key legal provisions, the courts/jurisdictions mentioned, any deadlines or timeframes, and the required procedures. Be thorough and specific.",
      "summary_en": "A DETAILED summary in English (6-8 sentences minimum). Include: the purpose of the document, the key legal provisions, the courts/jurisdictions mentioned, any deadlines or timeframes, and the required procedures. Be thorough and specific.",
      "key_points_ar": ["نقطة رئيسية 1", "نقطة رئيسية 2", "نقطة رئيسية 3", "نقطة رئيسية 4"],
      "key_points_en": ["Key point 1", "Key point 2", "Key point 3", "Key point 4"]
    }
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=4096
            )
        )
        return json.loads(response.text)

    except json.JSONDecodeError:
        st.error("Failed to parse JSON. Raw response:")
        st.write(response.text)
        return None
    except Exception as e:
        st.error(f"An error occurred with the API: {e}")
        return None


def convert_pdf_to_image(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    matrix = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=matrix)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return image


ARABIC_DOC_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Scheherazade+New:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .stApp {
        background: #fdfaf3;
        background-image:
            radial-gradient(circle at 20% 30%, rgba(212, 175, 55, 0.04) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(139, 69, 19, 0.03) 0%, transparent 50%);
    }

    html, body, [class*="css"] {
        font-family: 'Cairo', 'Segoe UI', sans-serif;
        color: #2b2b2b;
    }

    h1 {
        font-family: 'Amiri', serif !important;
        color: #1a3d2e !important;
        text-align: center;
        font-weight: 700 !important;
        letter-spacing: 1px;
        border-bottom: 3px double #d4af37;
        padding-bottom: 14px;
        margin-bottom: 8px;
    }

    .doc-subtitle {
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 15px;
        color: #6b5b3e;
        margin-bottom: 24px;
        font-style: italic;
    }

    .doc-field {
        background: #fffef9;
        border: 1px solid #e6dbb8;
        border-right: 6px solid #d4af37;
        border-radius: 6px;
        padding: 18px 24px;
        margin-bottom: 18px;
        box-shadow: 0 2px 5px rgba(139, 69, 19, 0.06);
        direction: rtl;
        text-align: right;
    }

    .doc-field-label {
        font-family: 'Amiri', serif;
        font-size: 15px;
        font-weight: 700;
        color: #8b4513;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px dashed #d4af37;
        direction: rtl;
    }

    .doc-field-ar {
        font-family: 'Amiri', 'Scheherazade New', serif;
        font-size: 19px;
        color: #1a1a1a;
        direction: rtl;
        text-align: right;
        line-height: 1.9;
        margin-bottom: 10px;
    }

    .doc-field-en {
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        color: #555;
        direction: ltr;
        text-align: left;
        padding-top: 10px;
        border-top: 1px dotted #ccc;
        line-height: 1.6;
    }

    .doc-summary {
        background: #fdf9ec;
        border: 1px solid #e6dbb8;
        border-radius: 6px;
        padding: 24px 28px;
        margin-bottom: 18px;
        box-shadow: 0 2px 5px rgba(139, 69, 19, 0.06);
    }

    .doc-summary-label {
        font-family: 'Amiri', serif;
        font-size: 17px;
        font-weight: 700;
        color: #8b4513;
        text-align: center;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 2px solid #d4af37;
        letter-spacing: 1px;
    }

    .doc-summary-ar {
        font-family: 'Amiri', serif;
        font-size: 17px;
        color: #1a1a1a;
        direction: rtl;
        text-align: justify;
        line-height: 2.2;
        margin-bottom: 16px;
    }

    .doc-summary-en {
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        color: #444;
        direction: ltr;
        text-align: justify;
        line-height: 1.8;
        padding-top: 14px;
        border-top: 1px dashed #d4af37;
    }

    .doc-kp {
        background: #f4f8f2;
        border: 1px solid #c8dcc0;
        border-right: 6px solid #4a7c59;
        border-radius: 6px;
        padding: 18px 24px;
        margin-bottom: 18px;
        direction: rtl;
    }

    .doc-kp-label {
        font-family: 'Amiri', serif;
        font-size: 16px;
        font-weight: 700;
        color: #2d5a3d;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px dashed #4a7c59;
    }

    .doc-kp ul {
        padding-right: 24px;
        padding-left: 0;
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', serif;
        font-size: 16px;
        line-height: 2;
        color: #1a1a1a;
        margin: 0;
    }

    .doc-kp-en ul {
        padding-left: 24px;
        padding-right: 0;
        direction: ltr;
        text-align: left;
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        line-height: 1.8;
        color: #333;
    }

    .doc-kp ul li {
        margin-bottom: 8px;
    }

    .ornament {
        text-align: center;
        color: #d4af37;
        font-size: 20px;
        letter-spacing: 12px;
        margin: 26px 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #1a3d2e 0%, #2d5a3d 100%);
        color: #fdfaf3;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        font-size: 15px;
        border: 2px solid #d4af37;
        border-radius: 6px;
        padding: 10px 28px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2d5a3d 0%, #1a3d2e 100%);
        border-color: #f0d97a;
        box-shadow: 0 4px 12px rgba(26, 61, 46, 0.3);
    }

    .stAlert {
        font-family: 'Cairo', sans-serif;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #1a3d2e 0%, #2d5a3d 100%) !important;
        color: #fdfaf3 !important;
        border: 2px solid #d4af37 !important;
        border-radius: 6px !important;
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 20px !important;
        position: relative !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(135deg, #2d5a3d 0%, #1a3d2e 100%) !important;
        border-color: #f0d97a !important;
    }

    [data-testid="stFileUploaderDropzone"] button div,
    [data-testid="stFileUploaderDropzone"] button p {
        color: #fdfaf3 !important;
        font-family: 'Cairo', sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Hide Streamlit's hidden accessibility span that causes "uploadpload" */
    [data-testid="stFileUploaderDropzone"] button > span {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzone"] button::before,
    [data-testid="stFileUploaderDropzone"] button::after {
        content: none !important;
        display: none !important;
    }
</style>
"""


def render_doc_field(label, ar_val, en_val):
    st.markdown(f"""
        <div class="doc-field">
            <div class="doc-field-label">◆ {label}</div>
            <div class="doc-field-ar">{ar_val}</div>
            <div class="doc-field-en">{en_val}</div>
        </div>
    """, unsafe_allow_html=True)


def render_summary(ar_val, en_val):
    st.markdown(f"""
        <div class="doc-summary">
            <div class="doc-summary-label">◆ الملخص ◆ SUMMARY ◆</div>
            <div class="doc-summary-ar">{ar_val}</div>
            <div class="doc-summary-en">{en_val}</div>
        </div>
    """, unsafe_allow_html=True)


def render_key_points(ar_points, en_points):
    ar_html = "".join([f"<li>{p}</li>" for p in ar_points])
    en_html = "".join([f"<li>{p}</li>" for p in en_points])

    st.markdown(f"""
        <div class="doc-kp">
            <div class="doc-kp-label">◆ النقاط الرئيسية | Key Points ◆</div>
            <ul>{ar_html}</ul>
        </div>
        <div class="doc-kp doc-kp-en">
            <ul>{en_html}</ul>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Arabic Document Extractor", layout="wide")
    st.markdown(ARABIC_DOC_CSS, unsafe_allow_html=True)

    col_logo, col_center, col_spacer = st.columns([1, 4, 1])

    with col_logo:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=130)
        else:
            st.warning(f"Logo not found at: {LOGO_PATH}")

    with col_center:
        st.markdown(
            '<h1 style="text-align:center; margin-top: 10px;">مستخرج المستندات القانونية</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="doc-subtitle" style="text-align:center;">Arabic Document Extractor</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="ornament">❖ ❖ ❖</div>', unsafe_allow_html=True)


    uploaded_file = st.file_uploader(
        "Upload an image or PDF | اختر مستنداً (صورة أو PDF)",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith('.pdf'):
                image = convert_pdf_to_image(uploaded_file)
            else:
                image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.stop()

        col_img, col_results = st.columns([1, 1])

        with col_img:
            st.markdown('<div class="doc-field-label">◆ المستند الأصلي | Original Document ◆</div>', unsafe_allow_html=True)
            st.image(image, caption='', width="stretch")

        with col_results:
            if st.button('استخراج المعلومات  |  Extract Information'):
                if not API_KEY:
                    st.error("Please add API_KEY to your .streamlit/secrets.toml file.")
                else:
                    placeholder = st.empty()
                    placeholder.markdown("""
                        <div style="
                            background: #fdf9ec;
                            border: 1px solid #e6dbb8;
                            border-right: 6px solid #d4af37;
                            border-radius: 6px;
                            padding: 22px;
                            text-align: center;
                            font-family: 'Amiri', serif;
                            box-shadow: 0 2px 5px rgba(139, 69, 19, 0.08);
                        ">
                            <div style="
                                font-size: 20px;
                                color: #8b4513;
                                margin-bottom: 10px;
                                font-weight: 700;
                            ">جاري تحليل المستند...</div>
                            <div style="
                                font-family: 'Cairo', sans-serif;
                                font-size: 15px;
                                color: #6b5b3e;
                            ">Analyzing document... Please wait</div>
                        </div>
                    """, unsafe_allow_html=True)

                    with st.spinner(''):
                        extracted_data = extract_info_with_gemini(image)

                    placeholder.empty()

                    if extracted_data:
                        st.success("Extraction Complete | اكتمل الاستخراج")

                        render_doc_field(
                            "رقم التعميم | Document ID",
                            extracted_data.get('id_ar', 'N/A'),
                            extracted_data.get('id_en', 'N/A')
                        )

                        render_doc_field(
                            "التاريخ | Date",
                            extracted_data.get('date_ar', 'N/A'),
                            extracted_data.get('date_en', 'N/A')
                        )

                        render_doc_field(
                            "الموضوع | Subject",
                            extracted_data.get('subject_ar', 'N/A'),
                            extracted_data.get('subject_en', 'N/A')
                        )

                        st.markdown('<div class="ornament">❖ ❖ ❖</div>', unsafe_allow_html=True)

                        render_summary(
                            extracted_data.get('summary_ar', 'N/A'),
                            extracted_data.get('summary_en', 'N/A')
                        )

                        render_key_points(
                            extracted_data.get('key_points_ar', []),
                            extracted_data.get('key_points_en', [])
                        )


if __name__ == "__main__":
    main()
