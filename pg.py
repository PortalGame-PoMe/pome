import json
import os
import math
import base64

PASSWORD = os.environ["PORTAL_PASSWORD"]
LIMIT = 60

FILES_TO_PROCESS = [
    {'input': 'PG_Ranking.json', 'sort_name': 'ranking'},
    {'input': 'PG_New.json', 'sort_name': 'new'}
]

def encrypt_data(data_dict, password):
    json_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    pass_bytes = password.strip().encode('utf-8')
    
    encrypted_bytes = bytearray()
    for i in range(len(json_bytes)):
        encrypted_bytes.append(json_bytes[i] ^ pass_bytes[i % len(pass_bytes)])
        
    return base64.b64encode(encrypted_bytes).decode('utf-8')

for file_info in FILES_TO_PROCESS:
    input_file = file_info['input']
    sort_name = file_info['sort_name']
    base_dir = f'bridge/pg/{sort_name}/'
    
    print(f"Membaca file {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ File {input_file} tidak ditemukan!")
        continue
        
    if isinstance(raw_data, dict) and 'items' in raw_data:
        raw_data = raw_data['items']
        
    seen_urls = set()
    all_games = []
    categories_dict = {}

    for g in raw_data:
        game_link = g.get('url', '')
        safe_url = game_link.rstrip('/').lower()
        
        if safe_url != "" and safe_url not in seen_urls:
            seen_urls.add(safe_url)
            
            cat = g.get('category', 'Game')
            
            formatted_game = {
                "id": g.get('id', ''),
                "title": g.get('title', ''),
                "url": g.get('url', ''),
                "thumb": g.get('thumb', ''),
                "video": g.get('video', ''),
                "category": cat,
                "provider": "playgama"
            }
            all_games.append(formatted_game)
            
            if cat not in categories_dict:
                categories_dict[cat] = []
            categories_dict[cat].append(formatted_game)

    categories_list = sorted(list(categories_dict.keys()))

    print(f"[{sort_name}] Proses folder All Games...")
    all_dir = os.path.join(base_dir, 'all')
    os.makedirs(all_dir, exist_ok=True)
    total_games = len(all_games)
    total_pages = math.ceil(total_games / LIMIT) if total_games > 0 else 1

    for page in range(1, total_pages + 1):
        start_index = (page - 1) * LIMIT
        end_index = start_index + LIMIT
        output_data = {
            "page": page,
            "total_games": total_games,
            "total_pages": total_pages,
            "categories": categories_list,
            "data": all_games[start_index:end_index]
        }
        
        encrypted_text = encrypt_data(output_data, PASSWORD)
        with open(os.path.join(all_dir, f'page-{page}.json'), 'w', encoding='utf-8') as out_f:
            out_f.write(encrypted_text)

    print(f"[{sort_name}] Proses file Kategori...")
    for cat_name, games_in_cat in categories_dict.items():
        safe_cat_folder = cat_name.replace('/', '_').replace('\\', '_').replace('.', '')
        cat_dir = os.path.join(base_dir, 'category', safe_cat_folder)
        os.makedirs(cat_dir, exist_ok=True)
        
        total_cat_games = len(games_in_cat)
        total_cat_pages = math.ceil(total_cat_games / LIMIT)
        
        for page in range(1, total_cat_pages + 1):
            start_index = (page - 1) * LIMIT
            end_index = start_index + LIMIT
            output_data = {
                "page": page,
                "total_games": total_cat_games,
                "total_pages": total_cat_pages,
                "categories": categories_list,
                "data": games_in_cat[start_index:end_index]
            }
            
            encrypted_text = encrypt_data(output_data, PASSWORD)
            with open(os.path.join(cat_dir, f'page-{page}.json'), 'w', encoding='utf-8') as out_f:
                out_f.write(encrypted_text)

    print(f"[{sort_name}] Proses file Master Pencarian...")
    search_dir = os.path.join(base_dir, 'search')
    os.makedirs(search_dir, exist_ok=True)
    
    encrypted_search_text = encrypt_data(all_games, PASSWORD)
    with open(os.path.join(search_dir, 'index.json'), 'w', encoding='utf-8') as out_f:
        out_f.write(encrypted_search_text)

print("✅ Proses Portal 4 Selesai!")