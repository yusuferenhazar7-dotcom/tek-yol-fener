import streamlit as st
import google.generativeai as genai
from newspaper import Article
from duckduckgo_search import DDGS
import os
import random
import re

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

girdi_turu = st.radio("Girdi Türü", ["Haber Linki", "Manuel Metin"])
girdi_verisi = st.text_area("Haber İçeriğini Girin", height=250)

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
                response = model.generate_content(f"{tarz_talimati}\n\nİçerik: {girdi_verisi}")
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
