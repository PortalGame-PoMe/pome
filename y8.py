import json, os, math, base64, re

PASSWORD = "${{ secrets.YOUR_PASSWORD }}"
INPUT_FILE = 'Y8_Cache.json'
BASE_DIR = 'pome/bridge/y8/'
LIMIT = 60

def encrypt_data(data_dict, password):
    json_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    pass_bytes = password.encode('utf-8')
    encrypted_bytes = bytearray()
    for i in range(len(json_bytes)):
        encrypted_bytes.append(json_bytes[i] ^ pass_bytes[i % len(pass_bytes)])
    return base64.b64encode(encrypted_bytes).decode('utf-8')

print("Membaca file Y8...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

seen_urls = set()
all_games = []
global_cats = set()
junk_words = ["front upload", "purchase equipment", "touchscreen", "game contest 2016", "gamedistribution.com", "gamemonetize", "gamepix", "gamepadsupport", "girl", "iap (in-app purchases)", "ideastudio", "internal games", "java", "not on kong", "nyan cat", "roxie kitchen", "unity web player", "video game", "witchhut.com", "y8 account", "y8 contest", "y8 save", "y8 screenshot", "_android", "free game", "freakx apps", "excluded on ios", "android only", "android game", "mobile", "ipad", "iphone", "html5", "webgl", "unity3d", "flash", "2 players"]

for g in raw_data:
    game_link = g.get('embed_url') or g.get('y8_url') or ''
    
    safe_url = game_link.strip()
    
    check_url = safe_url.split('?')[0].lower().rstrip('/')
    
    if safe_url != "" and check_url not in seen_urls:
        seen_urls.add(check_url)
        cat_list = [t.strip() for t in g.get('tags', '').split(',') if t.strip()]
        clean_cats = []
        for t in cat_list:
            t_low = t.lower()
            if not (any(j in t_low for j in ["front upload", "purchase equipment"]) or t_low in junk_words):
                clean_cats.append(t)
                global_cats.add(t)
        
        main_cat = clean_cats[0] if clean_cats else "Game"
        type_raw = g.get('type', '')
        try:
            t_arr = json.loads(type_raw) if type_raw.startswith('[') else [re.sub(r'\[|\]|"', '', type_raw).strip()]
        except:
            t_arr = [re.sub(r'\[|\]|"', '', type_raw).strip()] if type_raw else []
            
        formatted = {
            "id": re.sub(r'\s+', '-', g.get('title', '')).lower(),
            "title": g.get('title', ''), "url": safe_url, "thumb": g.get('poster', ''),
            "video": g.get('video', ''), "category": main_cat,
            "allCategories": clean_cats, "allTypes": [t.lower() for t in t_arr],
            "provider": "y8"
        }
        all_games.append(formatted)

cats_list = sorted(list(global_cats))
tot_games = len(all_games)
tot_pages = math.ceil(tot_games / LIMIT) if tot_games > 0 else 1

all_dir = os.path.join(BASE_DIR, 'all')
os.makedirs(all_dir, exist_ok=True)
for p in range(1, tot_pages + 1):
    start = (p - 1) * LIMIT
    paged = []
    for game in all_games[start:start+LIMIT]:
        g_copy = game.copy()
        g_copy.pop('allCategories', None)
        g_copy.pop('allTypes', None)
        paged.append(g_copy)
        
    out = {"page": p, "total_games": tot_games, "total_pages": tot_pages, "categories": cats_list, "data": paged}
    with open(os.path.join(all_dir, f'page-{p}.json'), 'w', encoding='utf-8') as f:
        f.write(encrypt_data(out, PASSWORD))

search_dir = os.path.join(BASE_DIR, 'search')
os.makedirs(search_dir, exist_ok=True)
with open(os.path.join(search_dir, 'index.json'), 'w', encoding='utf-8') as f:
    f.write(encrypt_data(all_games, PASSWORD))

print("✅ Y8 Selesai!")