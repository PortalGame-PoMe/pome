import json, os, math, base64

PASSWORD = os.environ["PORTAL_PASSWORD"]
LIMIT = 60

def encrypt_data(data_dict, password):
    json_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    pass_bytes = password.strip().encode('utf-8')
    encrypted_bytes = bytearray()
    for i in range(len(json_bytes)):
        encrypted_bytes.append(json_bytes[i] ^ pass_bytes[i % len(pass_bytes)])
    return base64.b64encode(encrypted_bytes).decode('utf-8')

CONFIGS = [
    {'file': 'GM_Cache.json', 'dir': 'bridge/gm/'},
    {'file': 'GM_Mobile_Cache.json', 'dir': 'bridge/gm/mobile/'}
]

for cfg in CONFIGS:
    print(f"\n🚀 Memproses: {cfg['file']}")
    try:
        with open(cfg['file'], 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("⚠️ File tidak ditemukan, lanjut ke file berikutnya...")
        continue
        
    seen_urls = set()
    all_games = []
    categories_dict = {}

    for g in raw_data:
        game_link = g.get('url', '')
        safe_url = game_link.rstrip('/').lower()
        if safe_url != "" and safe_url not in seen_urls:
            seen_urls.add(safe_url)
            cat = g.get('category', 'Game')
            formatted = {
                "id": g.get('id', ''), "title": g.get('title', ''), "url": g.get('url', ''),
                "thumb": g.get('thumb') or g.get('thumbnail_256x256') or g.get('image', ''),
                "category": cat
            }
            all_games.append(formatted)
            if cat not in categories_dict:
                categories_dict[cat] = []
            categories_dict[cat].append(formatted)

    cats_list = sorted(list(categories_dict.keys()))
    
    all_dir = os.path.join(cfg['dir'], 'all')
    os.makedirs(all_dir, exist_ok=True)
    tot_games = len(all_games)
    tot_pages = math.ceil(tot_games / LIMIT) if tot_games > 0 else 1
    
    for p in range(1, tot_pages + 1):
        start = (p - 1) * LIMIT
        out = {"page": p, "total_games": tot_games, "total_pages": tot_pages, "categories": cats_list, "data": all_games[start:start+LIMIT]}
        with open(os.path.join(all_dir, f'page-{p}.json'), 'w', encoding='utf-8') as f:
            f.write(encrypt_data(out, PASSWORD))
            
    for cat_name, games in categories_dict.items():
        safe_cat = cat_name.replace('/', '_').replace('\\', '_').replace('.', '')
        cat_dir = os.path.join(cfg['dir'], 'category', safe_cat)
        os.makedirs(cat_dir, exist_ok=True)
        t_games = len(games)
        t_pages = math.ceil(t_games / LIMIT)
        for p in range(1, t_pages + 1):
            start = (p - 1) * LIMIT
            out = {"page": p, "total_games": t_games, "total_pages": t_pages, "categories": cats_list, "data": games[start:start+LIMIT]}
            with open(os.path.join(cat_dir, f'page-{p}.json'), 'w', encoding='utf-8') as f:
                f.write(encrypt_data(out, PASSWORD))
                
    search_dir = os.path.join(cfg['dir'], 'search')
    os.makedirs(search_dir, exist_ok=True)
    with open(os.path.join(search_dir, 'index.json'), 'w', encoding='utf-8') as f:
        f.write(encrypt_data(all_games, PASSWORD))

print("\n✅ Proses Portal 1 Selesai!")