import streamlit as st
import google.generativeai as genai
from newspaper import Article
from duckduckgo_search import DDGS
import os
import re
import requests

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

st.set_page_config(page_title="Pro Haber Ajansı v35", layout="wide")
st.title("🗞️ Tam Donanımlı Profesyonel Spor Paneli")

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
        # URL'yi FxTwitter formatına çevir
        # https://x.com/user/status/123 -> https://api.fxtwitter.com/user/status/123
        # https://twitter.com/user/status/123 -> https://api.fxtwitter.com/user/status/123
        url = url.strip()
        if "x.com/" in url or "twitter.com/" in url:
            # Path kısmını çıkar
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
    
    # Twitter/X linki mi kontrol et
    if "x.com/" in url or "twitter.com/" in url:
        content = get_tweet_content(url)
        if content:
            return content, "twitter"
    
    # Normal haber sitesi
    content = get_article_content(url)
    if content:
        return content, "article"
    
    return None, None

girdi_turu = st.radio("Girdi Türü", ["Haber Linki", "Manuel Metin"])
girdi_verisi = st.text_area("Haber İçeriğini veya Link'i Girin (Twitter/X desteklenir)", height=250)

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

if st.button("Haberleri ve Görselleri Hazırla"):
    if not girdi_verisi:
        st.warning("İçerik girilmedi.")
    else:
        with st.spinner('Analiz ediliyor ve görseller optimize ediliyor...'):
            try:
                # İçeriği hazırla
                icerik = girdi_verisi
                
                # Eğer link girilmişse içeriği çek
                if girdi_turu == "Haber Linki" and girdi_verisi.startswith("http"):
                    extracted, source_type = extract_content_from_url(girdi_verisi)
                    if extracted:
                        icerik = extracted
                        if source_type == "twitter":
                            st.info(f"🐦 Tweet içeriği çekildi!")
                        else:
                            st.info(f"📰 Haber içeriği çekildi!")
                    else:
                        st.warning("Link'ten içerik çekilemedi. Manuel metin olarak işleniyor.")
                
                response = model.generate_content(f"{tarz_talimati}\n\nİçerik: {icerik}")
                tweetler = [t.strip() for t in response.text.split('---') if t.strip()]

                for idx, tweet_ham in enumerate(tweetler):
                    col1, col2 = st.columns([1.5, 1])
                    with col1:
                        st.subheader(f"Haber {idx+1}")
                        st.code(tweet_ham, language=None)
                        st.caption(f"Karakter: {len(tweet_ham)}/280")

                    with col2:
                        metin_low = tweet_ham.lower()
                        secilen_tk = next((k for t, k in TAKIMLAR.items() if t.lower() in metin_low), None)

                        if secilen_tk:
                            # 1. LOGO
                            l_img = find_image(f"{secilen_tk}_logo.png")
                            if l_img: st.image(l_img, use_container_width=True)

                            # 2. SON DAKİKA
                            if "#sondakika" in metin_low:
                                sd_img = find_image(f"{secilen_tk}_sd.png")
                                if sd_img: st.image(sd_img, caption="SON DAKİKA", use_container_width=True)

                            # 3. OYUNCU FOTOSU (İnternetten HD Çekim)
                            oyuncular = re.findall(r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)+)', tweet_ham)
                            if oyuncular:
                                p_img = get_player_image(oyuncular[0])
                                if p_img: st.image(p_img, caption=f"Foto: {oyuncular[0]}", use_container_width=True)

                            # 4. STANDART GÖRSEL
                            std_img = find_image(f"{secilen_tk}_std.png")
                            if std_img: st.image(std_img, use_container_width=True)
                        else:
                            st.info("Takım tespit edilemedi.")
                    st.markdown("---")
            except Exception as e:
                st.error(f"Hata: {e}")
