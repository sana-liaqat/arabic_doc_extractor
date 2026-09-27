import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import fitz  
import io

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except KeyError:
    API_KEY = None
    client = None
    st.error("⚠️ API_KEY not found in secrets.toml. Please set it up.")


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
      "summary_ar": "A DETAILED summary in Arabic (7-8 sentences minimum). Include: the purpose of the document, the key legal provisions, the courts/jurisdictions mentioned, any deadlines or timeframes, and the required procedures. Be thorough and specific.",
      "summary_en": "A DETAILED summary in English (8-6 sentences minimum). Include: the purpose of the document, the key legal provisions, the courts/jurisdictions mentioned, any deadlines or timeframes, and the required procedures. Be thorough and specific.",
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

        data = json.loads(response.text)
        return data

    except json.JSONDecodeError:
        st.error("Failed to parse JSON. Raw response:")
        st.write(response.text)
        return None
    except Exception as e:
        st.error(f"An error occurred with the API: {e}")
        return None


def convert_pdf_to_image(pdf_file):
    """Convert the first page of a PDF to a PIL Image using PyMuPDF (no Poppler needed)."""
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    matrix = fitz.Matrix(2.0, 2.0)  # 2x zoom for higher DPI
    pix = page.get_pixmap(matrix=matrix)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return image


def main():
    st.set_page_config(page_title="Arabic Document Extractor", layout="wide")

    st.title("Arabic Doc Extractor | مستخرج المستندات")
    st.markdown("Upload an image or PDF of the document. We will extract the details in both Arabic and English.")

    uploaded_file = st.file_uploader(
        "Choose an image or PDF...",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    if uploaded_file is not None:
        # Handle PDF vs Image
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
            st.image(image, caption='Uploaded Document (First Page)', width="stretch")

        with col_results:
            if st.button('Extract Information | استخراج المعلومات'):
                if not API_KEY:
                    st.error("Please add API_KEY to your .streamlit/secrets.toml file.")
                else:
                    with st.spinner('We are analyzing the document...'):
                        extracted_data = extract_info_with_gemini(image)

                        if extracted_data:
                            st.success("Extraction Complete!")

                            # --- Document ID ---
                            st.markdown("### Document ID | رقم التعميم")
                            st.info(
                                f"🇸🇦 {extracted_data.get('id_ar', 'N/A')}   |   "
                                f"🇬🇧 {extracted_data.get('id_en', 'N/A')}"
                            )

                            # --- Date ---
                            st.markdown("### Date | التاريخ")
                            st.info(
                                f"🇸🇦 {extracted_data.get('date_ar', 'N/A')}   |   "
                                f"🇬🇧 {extracted_data.get('date_en', 'N/A')}"
                            )

                            # --- Subject ---
                            st.markdown("### Subject | الموضوع")
                            st.info(
                                f"🇸🇦 {extracted_data.get('subject_ar', 'N/A')}\n\n"
                                f"🇬🇧 {extracted_data.get('subject_en', 'N/A')}"
                            )

                            # --- Summary ---
                            st.markdown("### Summary | الملخص")
                            st.warning(
                                f"🇬🇧 **English:**\n\n{extracted_data.get('summary_en', 'N/A')}\n\n"
                                f"---\n\n"
                                f"🇸🇦 **بالعربية:**\n\n{extracted_data.get('summary_ar', 'N/A')}"
                            )

                            # --- Key Points ---
                            st.markdown("### Key Points | النقاط الرئيسية")
                            col_ar, col_en = st.columns(2)
                            with col_ar:
                                st.markdown("**🇸🇦 بالعربية:**")
                                for point in extracted_data.get('key_points_ar', []):
                                    st.markdown(f"- {point}")
                            with col_en:
                                st.markdown("**🇬🇧 In English:**")
                                for point in extracted_data.get('key_points_en', []):
                                    st.markdown(f"- {point}")


if __name__ == "__main__":
    main()