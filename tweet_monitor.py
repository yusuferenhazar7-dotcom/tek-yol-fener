"""
Twitter Auto-Monitor Script
Her saat çalışıp @tekyolfener tweetlerini analiz eder
"""
import json
import os
import re
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Takip edilecek hesaplar
ACCOUNTS = ["tekyolfener"]

# Dosya yolları
ARCHIVE_FILE = Path(__file__).parent / "tweets_archive.json"

def fetch_tweets(username: str) -> list:
    """Twitter Syndication API ile tweetleri çek"""
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # HTML response'dan JSON'u çıkar
        html = response.text
        
        # __NEXT_DATA__ script tag'inden JSON'u bul
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html)
        if not match:
            print(f"Could not find tweet data for @{username}")
            return []
        
        data = json.loads(match.group(1))
        entries = data.get("props", {}).get("pageProps", {}).get("timeline", {}).get("entries", [])
        
        tweets = []
        for entry in entries:
            if entry.get("type") == "tweet":
                tweet = entry.get("content", {}).get("tweet", {})
                tweets.append({
                    "id": tweet.get("id_str"),
                    "text": tweet.get("full_text", tweet.get("text", "")),
                    "created_at": tweet.get("created_at"),
                    "username": username,
                    "likes": tweet.get("favorite_count", 0),
                    "retweets": tweet.get("retweet_count", 0),
                    "url": f"https://x.com/{username}/status/{tweet.get('id_str')}"
                })
        
        return tweets
        
    except Exception as e:
        print(f"Error fetching tweets for @{username}: {e}")
        return []

def filter_recent_tweets(tweets: list, hours: int = 1) -> list:
    """Son X saat içindeki tweetleri filtrele"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    
    for tweet in tweets:
        try:
            # Twitter tarih formatı: "Sat Feb 25 15:58:21 +0000 2023"
            created = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y")
            if created > cutoff:
                tweet["created_parsed"] = created.isoformat()
                recent.append(tweet)
        except (ValueError, TypeError):
            continue
    
    return recent

def analyze_with_gemini(tweets: list) -> list:
    """Gemini ile haber değeri analizi"""
    if not GEMINI_AVAILABLE or not os.environ.get("GEMINI_API_KEY"):
        print("Gemini not available, returning all tweets")
        for tweet in tweets:
            tweet["is_newsworthy"] = True
            tweet["news_summary"] = tweet["text"][:200]
        return tweets
    
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    analyzed = []
    for tweet in tweets:
        prompt = f"""
Bu tweet haber değeri taşıyor mu? Fenerbahçe ile ilgili önemli bir gelişme, transfer, maç sonucu, 
resmi açıklama veya önemli bir haber mi?

Tweet: {tweet['text']}

JSON formatında yanıt ver:
{{"is_newsworthy": true/false, "reason": "kısa açıklama", "suggested_headline": "varsa başlık önerisi"}}
"""
        try:
            response = model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            tweet["is_newsworthy"] = result.get("is_newsworthy", False)
            tweet["news_summary"] = result.get("suggested_headline", tweet["text"][:200])
            tweet["analysis_reason"] = result.get("reason", "")
            analyzed.append(tweet)
        except Exception as e:
            print(f"Error analyzing tweet: {e}")
            tweet["is_newsworthy"] = False
            analyzed.append(tweet)
    
    return analyzed

def load_archive() -> dict:
    """Mevcut arşivi yükle"""
    if ARCHIVE_FILE.exists():
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"tweets": [], "last_updated": None}

def save_archive(archive: dict):
    """Arşivi kaydet"""
    archive["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

def main():
    print(f"🔍 Tweet Monitor başlatıldı: {datetime.now(timezone.utc).isoformat()}")
    
    archive = load_archive()
    existing_ids = {t["id"] for t in archive["tweets"]}
    new_tweets = []
    
    for username in ACCOUNTS:
        print(f"\n📡 @{username} taranıyor...")
        tweets = fetch_tweets(username)
        print(f"   Toplam {len(tweets)} tweet bulundu")
        
        # Son 1 saat filtresi (GitHub Actions'da aktif olacak)
        # Şimdilik tüm tweetleri al (test için)
        recent = tweets  # filter_recent_tweets(tweets, hours=1)
        print(f"   Son dönem: {len(recent)} tweet")
        
        # Yeni tweetleri filtrele
        for tweet in recent:
            if tweet["id"] not in existing_ids:
                new_tweets.append(tweet)
    
    print(f"\n🆕 {len(new_tweets)} yeni tweet bulundu")
    
    if new_tweets:
        # Gemini analizi
        analyzed = analyze_with_gemini(new_tweets)
        newsworthy = [t for t in analyzed if t.get("is_newsworthy")]
        print(f"📰 {len(newsworthy)} haber değeri taşıyan tweet")
        
        # Arşive ekle
        archive["tweets"].extend(newsworthy)
        
        # Son 100 tweet tut
        archive["tweets"] = archive["tweets"][-100:]
        
        save_archive(archive)
        print(f"💾 Arşiv güncellendi: {ARCHIVE_FILE}")
    else:
        print("⏳ Yeni tweet yok")
    
    print("\n✅ Tamamlandı")

if __name__ == "__main__":
    main()
