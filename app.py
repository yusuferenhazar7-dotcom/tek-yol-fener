import streamlit as st
import google.generativeai as genai
from newspaper import Article
from duckduckgo_search import DDGS
import os
import re
import requests

# --- PROFESYONEL CSS TEMASI ---
st.set_page_config(
    page_title="Tek Yol Fener | Haber Ajansı",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Ana tema renkleri - Fenerbahçe sarı-lacivert */
    :root {
        --primary-color: #1a237e;
        --secondary-color: #ffd600;
        --bg-dark: #0a0e1a;
        --bg-card: #121828;
        --text-primary: #ffffff;
        --text-secondary: #b0b8c4;
        --accent-gradient: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #ffd600 100%);
    }
    
    /* Ana arka plan */
    .stApp {
        background: linear-gradient(180deg, #0a0e1a 0%, #1a1f2e 100%);
    }
    
    /* Başlık stili */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(26, 35, 126, 0.3);
        border: 1px solid rgba(255, 214, 0, 0.2);
    }
    
    .main-header h1 {
        color: #ffd600 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #ffffff;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Kart stilleri */
    .news-card {
        background: linear-gradient(145deg, #121828 0%, #1a2035 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 214, 0, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(255, 214, 0, 0.15);
        border-color: rgba(255, 214, 0, 0.3);
    }
    
    /* Input alanları */
    .stTextArea textarea {
        background-color: #121828 !important;
        border: 2px solid #2a3f5f !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ffd600 !important;
        box-shadow: 0 0 20px rgba(255, 214, 0, 0.2) !important;
    }
    
    /* Radio butonları */
    .stRadio > div {
        background: #121828;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #2a3f5f;
    }
    
    .stRadio label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Ana buton */
    .stButton > button {
        background: linear-gradient(135deg, #ffd600 0%, #ffab00 100%) !important;
        color: #1a237e !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 214, 0, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(255, 214, 0, 0.5) !important;
    }
    
    /* Kod bloğu (haber metni) */
    .stCode {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }
    
    code {
        color: #e6edf3 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    /* Karakter sayacı */
    .char-counter {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .char-ok {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    .char-warning {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }
    
    .char-danger {
        background: rgba(244, 67, 54, 0.2);
        color: #f44336;
        border: 1px solid rgba(244, 67, 54, 0.3);
    }
    
    /* Subheader */
    .stSubheader {
        color: #ffd600 !important;
    }
    
    h2, h3 {
        color: #ffd600 !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 12px !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 214, 0, 0.2) !important;
        margin: 2rem 0 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2a3f5f;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ffd600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 214, 0, 0.1);
    }
    
    /* Haber numarası badge */
    .news-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        color: #ffd600;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🦅 TEK YOL FENER</h1>
    <p>Profesyonel Spor Haber Ajansı</p>
</div>
""", unsafe_allow_html=True)

# Gemini Ayarı
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if "1.5-flash" in m: return m
        return models[0] if models else "models/gemini-1.5-flash"
    except: return "models/gemini-1.5-flash"

ACTIVE_MODEL = get_working_model()
model = genai.GenerativeModel(ACTIVE_MODEL)

# --- YAPILANDIRMA ---
TAKIMLAR = {"Fenerbahçe": "fb", "Galatasaray": "gs", "Beşiktaş": "bjk", "Trabzonspor": "ts"}

def find_image(file_name):
    try:
        files = os.listdir('.')
        for f in files:
            if f.lower() == file_name.lower(): return f
    except: return None
    return None

def get_player_image(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(f"{query} football player", max_results=1))
            if results: return results[0]['image']
    except: return None
    return None

def get_tweet_content(url):
    """Twitter/X linkinden tweet içeriğini çeker (FxTwitter API)"""
    try:
        url = url.strip()
        if "x.com/" in url or "twitter.com/" in url:
            if "x.com/" in url:
                path = url.split("x.com/")[1]
            else:
                path = url.split("twitter.com/")[1]
            
            api_url = f"https://api.fxtwitter.com/{path}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "tweet" in data:
                    tweet = data["tweet"]
                    author = tweet.get("author", {}).get("screen_name", "Bilinmiyor")
                    text = tweet.get("text", "")
                    return f"@{author}: {text}"
        return None
    except Exception as e:
        return None

def get_article_content(url):
    """Haber sitesinden makale içeriğini çeker"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

def extract_content_from_url(url):
    """URL'den içerik çeker - Twitter veya haber sitesi"""
    url = url.strip()
    
    if "x.com/" in url or "twitter.com/" in url:
        content = get_tweet_content(url)
        if content:
            return content, "twitter"
    
    content = get_article_content(url)
    if content:
        return content, "article"
    
    return None, None

def get_char_class(length):
    """Karakter sayısına göre CSS sınıfı döndür"""
    if length <= 250:
        return "char-ok"
    elif length <= 280:
        return "char-warning"
    else:
        return "char-danger"

# --- ANA ARAYÜZ ---
col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    girdi_turu = st.radio("📝 Girdi Türü", ["Haber Linki", "Manuel Metin"], horizontal=True)

with col_input2:
    st.markdown("##### 💡 İpucu")
    st.caption("Twitter/X ve haber sitesi linkleri desteklenir")

girdi_verisi = st.text_area(
    "Haber İçeriğini veya Link'i Girin",
    height=200,
    placeholder="https://x.com/... veya haber metnini buraya yapıştırın..."
)

# KAYNAK FORMATI GÜNCELLENMİŞ TALİMAT
tarz_talimati = """
Metni analiz et ve konuları '---' ile ayır. 100 habere kadar tek tek işle.

KRİTİK KURALLAR:
1. KAYNAK GÖSTERİMİ: Her haberin sonuna MUTLAKA kaynağı parantez içinde şu formatta ekle: (Kişi - Kurum).
   Örn: (Yağız Sabuncuoğlu - Sports Digitale) veya (Nevzat Dindar - Vole).
2. KARAKTER: Max 280 (Kaynak dahil).
3. EMOJİ: Yasak.
4. ETİKET: Önemli haberlerin başına '#SONDAKİKA | ' ekle.
"""

st.markdown("")
if st.button("🚀 Haberleri ve Görselleri Hazırla", use_container_width=True):
    if not girdi_verisi:
        st.warning("⚠️ İçerik girilmedi.")
    else:
        with st.spinner('🔄 Analiz ediliyor ve görseller hazırlanıyor...'):
            try:
                icerik = girdi_verisi
                
                if girdi_turu == "Haber Linki" and girdi_verisi.startswith("http"):
                    extracted, source_type = extract_content_from_url(girdi_verisi)
                    if extracted:
                        icerik = extracted
                        if source_type == "twitter":
                            st.success("🐦 Tweet içeriği başarıyla çekildi!")
                        else:
                            st.success("📰 Haber içeriği başarıyla çekildi!")
                    else:
                        st.warning("⚠️ Link'ten içerik çekilemedi. Manuel metin olarak işleniyor.")
                
                response = model.generate_content(f"{tarz_talimati}\n\nİçerik: {icerik}")
                tweetler = [t.strip() for t in response.text.split('---') if t.strip()]

                st.markdown("---")
                st.markdown("### 📋 Hazırlanan Haberler")
                
                for idx, tweet_ham in enumerate(tweetler):
                    col1, col2 = st.columns([1.5, 1])
                    
                    with col1:
                        char_len = len(tweet_ham)
                        char_class = get_char_class(char_len)
                        
                        st.markdown(f'<span class="news-badge">Haber #{idx+1}</span>', unsafe_allow_html=True)
                        st.code(tweet_ham, language=None)
                        st.markdown(
                            f'<span class="char-counter {char_class}">{char_len}/280 karakter</span>',
                            unsafe_allow_html=True
                        )

                    with col2:
                        metin_low = tweet_ham.lower()
                        secilen_tk = next((k for t, k in TAKIMLAR.items() if t.lower() in metin_low), None)

                        if secilen_tk:
                            l_img = find_image(f"{secilen_tk}_logo.png")
                            if l_img: st.image(l_img, use_container_width=True)

                            if "#sondakika" in metin_low:
                                sd_img = find_image(f"{secilen_tk}_sd.png")
                                if sd_img: st.image(sd_img, caption="🔴 SON DAKİKA", use_container_width=True)

                            oyuncular = re.findall(r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)+)', tweet_ham)
                            if oyuncular:
                                p_img = get_player_image(oyuncular[0])
                                if p_img: st.image(p_img, caption=f"📸 {oyuncular[0]}", use_container_width=True)

                            std_img = find_image(f"{secilen_tk}_std.png")
                            if std_img: st.image(std_img, use_container_width=True)
                        else:
                            st.info("ℹ️ Takım tespit edilemedi.")
                    
                    st.markdown("---")
                    
            except Exception as e:
                st.error(f"❌ Hata: {e}")

# Footer
st.markdown("""
<div class="footer">
    <p>🦅 Tek Yol Fener | Profesyonel Spor Haber Ajansı</p>
    <p>Twitter/X desteği ile geliştirilmiştir</p>
</div>
""", unsafe_allow_html=True)
