import requests
import re
import json
from datetime import datetime, timezone, timedelta

url = 'https://syndication.twitter.com/srv/timeline-profile/screen-name/tekyolfener'
response = requests.get(url, timeout=30)
html = response.text

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html)
if match:
    data = json.loads(match.group(1))
    entries = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    print(f'Simdi (UTC): {datetime.now(timezone.utc)}')
    print(f'Cutoff: {cutoff}')
    print(f'Toplam entry: {len(entries)}')
    
    for entry in entries[:10]:
        if entry.get('type') == 'tweet':
            tweet = entry.get('content', {}).get('tweet', {})
            created = tweet.get('created_at', '')
            text = tweet.get('full_text', tweet.get('text', ''))[:80]
            print(f'Tweet: {created}')
            print(f'  Text: {text}...')
            
            # Parse date
            try:
                parsed = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
                is_recent = parsed > cutoff
                print(f'  Parsed: {parsed} | Recent: {is_recent}')
            except Exception as e:
                print(f'  Parse error: {e}')
            print()
else:
    print('Data bulunamadi')
