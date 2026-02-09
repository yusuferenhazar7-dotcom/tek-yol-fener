# Tek Yol Fener - Streamlit Cloud Deployment

## ✅ Hazır Dosyalar
- `app.py` - Streamlit uygulaması
- `requirements.txt` - Bağımlılıklar
- `.gitignore` - Git için
- Git repo başlatıldı ✓

---

## 1. GitHub'da Repo Oluştur

1. **Aç:** https://github.com/new
2. **Repository name:** `tek-yol-fener`
3. **Public** seç (Streamlit Cloud ücretsiz için gerekli)
4. ❌ README ekleme (zaten dosyalarımız var)
5. **Create repository** tıkla

---

## 2. Kodu GitHub'a Yükle

Repo oluşturduktan sonra PowerShell'de çalıştır:

```powershell
cd "c:\Users\Admin\dev\tek yol fener"
git remote add origin https://github.com/KULLANICI_ADIN/tek-yol-fener.git
git branch -M main
git push -u origin main
```

> ⚠️ `KULLANICI_ADIN` kısmını kendi GitHub kullanıcı adınla değiştir!

---

## 3. Streamlit Cloud'a Deploy

1. **Aç:** https://share.streamlit.io
2. **Sign in with GitHub** ile giriş yap
3. **New app** tıkla
4. Ayarlar:
   - **Repository:** `KULLANICI_ADIN/tek-yol-fener`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. **Advanced settings** aç:
   - **Secrets** bölümüne ekle:
     ```
     GEMINI_API_KEY = "AIzaSyD86TgSFansGSGIcXXTmn17tLTq1bHgP5o"
     ```
6. **Deploy!** tıkla

---

## 4. Görselleri Ekleme

Logo ve görselleri eklemek için:
1. Dosyaları proje klasörüne koy
2. Git'e ekle ve push et:
```powershell
git add .
git commit -m "Add images"
git push
```

Streamlit Cloud otomatik olarak yeniden deploy eder.

---

## Beklenen URL
Deploy tamamlandığında şöyle bir URL alacaksın:
`https://KULLANICI_ADIN-tek-yol-fener-app-xxxxx.streamlit.app`
