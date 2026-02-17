import streamlit as st
from groq import Groq
import openai
import json
from PIL import Image
from io import BytesIO

# -----------------------------
# 1. PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Style Mate", layout="wide", page_icon="🏇")

# -----------------------------
# 2. DARK PURPLE THEME CSS
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;600&display=swap');

/* Global Dark Purple Theme */
html, body, [class*="css"], .main { 
    background-color: #1A0D2B !important;
    color: #EAE6FF !important;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #2E1A4A !important;
    border-right: 1px solid #5D3B8C;
}
[data-testid="stSidebar"] *, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #EAE6FF !important;
}

/* Headings */
h1, h2, h3, h4 { 
    font-family: 'Bodoni Moda', serif !important; 
    color: #CDA7FF !important;
    text-transform: none;
    letter-spacing: -0.5px;
}

/* Cards */
.detail-card {
    background: #2E1A4A; 
    padding: 25px; 
    border: 1px solid #5D3B8C;
    margin-bottom: 20px; 
    border-radius: 8px;
    box-shadow: 0 0 15px rgba(0,0,0,0.5);
    color: #EAE6FF;
}
.mix-card {
    background: #3B1F5E; 
    padding: 20px; 
    border-top: 3px solid #CDA7FF; 
    margin-bottom: 15px; 
    font-size: 0.95rem; 
    color: #EAE6FF; 
    font-style: italic;
}

/* Social Box */
.insta-box {
    background: #2E1A4A; 
    border: 1px solid #CDA7FF;
    color: #EAE6FF; 
    padding: 15px; 
    margin-top: 15px; 
    text-align: center; 
    font-family: 'Bodoni Moda', serif;
}

/* Buttons */
div.stButton > button {
    background-color: #5D3B8C;
    color: #EAE6FF; 
    border-radius: 5px; 
    border: none;
    padding: 15px 30px; 
    font-family: 'Bodoni Moda', serif;
    font-size: 1.1rem; 
    width: 100%; 
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #CDA7FF;
    color: #1A0D2B;
}

/* Inputs */
.stTextInput>div>div>input, 
.stSelectbox>div>div>div {
    background-color: #3B1F5E !important;
    border: 1px solid #5D3B8C !important;
    border-radius: 5px !important;
    color: #EAE6FF !important;
}

/* Divider Color */
hr {
    border-color: #5D3B8C;
}

/* Links */
a {
    color: #C5A059;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. API KEYS (replace with your keys)
# -----------------------------
GROQ_API_KEY = "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"
OPENAI_API_KEY = "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"

client_groq = Groq(api_key=GROQ_API_KEY)
openai.api_key = OPENAI_API_KEY

# -----------------------------
# 4. SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #CDA7FF;'>Style Mate</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; font-style: italic;'>Est. 2026</p>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("Personal Wardrobe")
    wardrobe_pic = st.file_uploader("Upload an heirloom or staple", type=["jpg", "png"])
    
    st.divider()
    st.subheader("Curation Details")
    gender = st.selectbox("Gender", ["Women", "Men", "Unisex"])
    occasion = st.text_input("Occasion", placeholder="e.g. Polo Match or Yacht Club")
    style_pref = st.text_input("Style Preference", placeholder="e.g. Quiet Luxury, Preppy")
    base_color = st.color_picker("Heritage Color", "#C5A059")
    budget = st.select_slider("Investment Range", options=["Modest", "Mid-Range", "High-End Luxury"])
    
    st.divider()
    generate = st.button("CURATE COLLECTION")

# -----------------------------
# 5. MAIN CONTENT
# -----------------------------
st.title("Style Mate")
st.write("#### _The Private Curation Service_")
st.divider()

def generate_looks():
    if not occasion or not style_pref:
        st.warning("Please provide your occasion and preferred aesthetic.")
        return

    # -----------------------------
    # 6. ENHANCED STYLIST PROMPT
    # -----------------------------
    wardrobe_context = "Integrate the uploaded item seamlessly into the suggested outfits, complementing colors and style." if wardrobe_pic else "Assume high-quality basics like cashmere sweaters, linen shirts, tailored trousers."
    
    system_msg = """
    You are a world-class fashion stylist, expert in quiet luxury, preppy, and high-society fashion.
    Your goal is to provide highly curated outfit suggestions tailored to the user's preferences, gender, occasion, and uploaded wardrobe item.
    Consider:
    - Color harmony, matching the user's chosen heritage/base color.
    - Material quality (cashmere, silk, linen, leather, high-end denim).
    - Timeless, classy, and context-appropriate pieces.
    - Accessory selection that elevates the outfit subtly (watches, pearls, belts, scarves).
    - Footwear suitable for occasion and outfit style.
    - Grooming tips for a polished appearance.
    - Include practical shopping links for investment pieces.
    Return ONLY valid JSON with keys:
    daily_mix, elite_upgrade, accessories, footwear, grooming, shopping_list, captions, image_prompt.
    """

    user_msg = f"""
    {wardrobe_context}
    Curate a {style_pref} look for {gender} attending {occasion}. Focus on timeless, classic materials.
    
    Example:
    daily_mix: "White linen shirt + tailored beige trousers + brown loafers..."
    elite_upgrade: "Italian cashmere blazer, silk tie, Hermès leather shoes..."
    accessories: "Minimalist watch, pearl earrings..."
    footwear: "Brown leather loafers, classic sneakers for casual..."
    grooming: "Neat hair, clean shave or manicured nails..."
    shopping_list: [{{"name": "Cashmere Sweater", "price": "$450"}}]
    captions: ["Effortless elegance for every occasion."]
    image_prompt: "Editorial fashion photography with luxurious lighting and estate background"
    
    Return JSON only.
    """

    # -----------------------------
    # 7. CALL GROQ AI
    # -----------------------------
    with st.spinner("Our tailors are preparing your look..."):
        try:
            res = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":system_msg},{"role":"user","content":user_msg}],
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
        except Exception as e:
            st.error(f"Stylist service unavailable: {e}")
            return

        col_viz, col_details = st.columns([1.2, 1], gap="large")

        # -----------------------------
        # 8. IMAGE PREVIEW
        # -----------------------------
        with col_viz:
            st.subheader("Editorial Preview")
            try:
                img_res = openai.images.generate(
                    model="dall-e-3",
                    prompt=f"Cinematic fashion editorial, {data['image_prompt']}, soft natural lighting, high-end textures, colors ivory and {base_color}",
                    size="1024x1024"
                )
                st.image(img_res.data[0].url, use_container_width=True)
            except:
                st.warning("Private gallery unavailable. See stylist report below.")

            # Instagram captions
            st.markdown("#### Instagram Caption")
            for caption in data.get("captions", []):
                st.markdown(f'<div class="insta-box"><em>{caption}</em></div>', unsafe_allow_html=True)

        # -----------------------------
        # 9. STYLIST REPORT
        # -----------------------------
        with col_details:
            st.subheader("The Stylist's Report")
            st.markdown("#### 🏇 The Daily Mix")
            st.markdown(f'<div class="mix-card">{data.get("daily_mix","")}</div>', unsafe_allow_html=True)
            
            st.markdown("#### 🏛️ The Elite Upgrade")
            st.markdown(f'<div class="detail-card">{data.get("elite_upgrade","")}</div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("#### _The Finishing Touches_")
            st.write(f"**Footwear:** {data.get('footwear','')}")
            st.write(f"**Accessories:** {data.get('accessories','')}")
            st.write(f"**Grooming:** {data.get('grooming','')}")
            
            st.divider()
            st.subheader("Investment Pieces")
            for item in data.get('shopping_list', []):
                search_url = f"https://www.google.com/search?q={item['name'].replace(' ', '+')}+buy"
                st.markdown(f"""
                    <div style="margin-bottom:15px; border-bottom: 1px solid #E0D8C3; padding-bottom: 10px;">
                        <span style="font-family: 'Bodoni Moda', serif; font-size: 1.1rem;">{item['name']}</span> — <span style="color: #354A21;">{item['price']}</span><br>
                        <a href="{search_url}" target="_blank" style="color:#C5A059; text-decoration:none; font-size:0.8rem; font-weight: bold;">INQUIRE ONLINE →</a>
                    </div>
                """, unsafe_allow_html=True)

if generate:
    generate_looks()
else:
    st.info("Welcome to Style Mate. Please define your preferences in the sidebar to begin your curation.")



