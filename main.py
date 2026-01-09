import json
import re
from requests import request
from unicodedata import category

if __name__ == "__main__":
    """
    用來給法規資料庫的條款進行預處理
    將每個條都加入編章節以增加關聯性
    """

    res = request(method="GET", url="http://127.0.0.1:8000/police/police_law/75/")
    law_obj = res.json()

    raw_data = law_obj['content']  # 你的原始資料
    processed_list = []  # 已處理的清單
    current_part: str = ""  # 編
    current_chapter: str = ""  # 章
    current_section: str = ""  # 節

    law_name = law_obj['law_name']  # 法規名稱
    law_class = law_obj['law_class']  # 法規層級
    category_name = law_obj['cate_name']  # 法規類別
    version = law_obj['release_date']  # 法規版本（修正日期）

    for item in raw_data:
        article = item['article'].strip()
        text = item['text'].strip()
        if not text:
            # 處理篇章節的特例
            if '編' in article:
                current_part = article
            elif '章' in article:
                current_chapter = article
            elif '節' in article:
                current_section = article
            continue

        # 清洗文本
        clean_text = text.replace('<br>', '\n').strip()

        # 建立基礎結構
        entry = {
            'part': current_part,
            'chapter': current_chapter,
            'section': current_section,
            'article': article,
            'text': clean_text
        }
        processed_list.append(entry)

    output = {
        'law_name': law_name,
        'law_class': law_class,
        'category_name': category_name,
        'version': version,
        'content': processed_list,
    }

    with open(f'{law_name}.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
