import json
from collections import Counter
import re

with open("pokemon_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

others = []
for card in data:
    if len(card["tags"]) > 1:
        if card["tags"][1] == "その他":
            others.append(card["title"])
    else:
        if card["tags"][0] == "その他":
            others.append(card["title"])

print(f"その他タグのカード：{len(others)}件")
print("=" * 50)

# タイトルから単語を抽出して頻出ワードを表示
words = []
for title in others:
    title = re.sub(r'[^a-zA-Z\s]', '', title.upper())
    for word in title.split():
        if len(word) > 3 and word not in ['POKEMON', 'CARD', 'JAPANESE', 'MINT', 'HOLO', 'RARE', 'PROMO', 'VINTAGE', 'WITH', 'FROM', 'FULL', 'HYPER', 'SUPER', 'ULTRA', 'SPECIAL', 'GRADED', 'GRADE', 'CARDS', 'ITEM', 'GAME']:
            words.append(word)

print("頻出ワードTOP30（辞書に追加すべき候補）：")
for word, count in Counter(words).most_common(30):
    print(f"  {word}: {count}件")