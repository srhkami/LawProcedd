import re


def convert_interpretations_to_md(input_text):
    lines = input_text.strip().split('\n')

    # 儲存結果的列表
    parsed_data = []

    # 狀態變數
    current_article_num = "未知"  # 紀錄當前最新的條號
    current_title = None  # 紀錄當前 ▲ 後的標題
    current_content = []  # 收集 ▲ 下方的內容

    # 正規表達式：匹配「第 X 條」
    # \s* 允許「第」與數字、數字與「條」之間有空白
    article_pattern = re.compile(r"^第\s*(\d+)\s*條")

    def save_current_block():
        """輔助函式：將目前暫存的內容寫入結果列表"""
        if current_title and current_content:
            # 組合內容並清理空白
            full_content = "\n".join([line.strip() for line in current_content if line.strip()])
            if full_content:
                parsed_data.append({
                    "meta": f"道路交通管理處罰條例第{current_article_num}條",
                    "title": current_title,
                    "content": full_content
                })

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. 檢查是否為「第 X 條」 (更新元數據來源)
        article_match = article_pattern.match(line)
        if article_match:
            # 在進入新法條前，先儲存上一筆函釋(如果有的話)
            save_current_block()

            # 更新當前條號
            current_article_num = article_match.group(1)

            # 重置函釋狀態 (因為這是法條原文，我們要捨棄，且這代表上一則函釋結束)
            current_title = None
            current_content = []
            continue

        # 2. 檢查是否為「▲」開頭 (新的函釋標題)
        if line.startswith("▲"):
            # 在進入新函釋前，先儲存上一筆函釋
            save_current_block()

            # 設定新的標題 (去除 ▲)
            current_title = line[1:].strip()
            current_content = []  # 清空內容暫存，準備接收新內容
            continue

        # 3. 如果當前有「函釋標題」正在作用中，則這行是內容
        if current_title is not None:
            current_content.append(line)

        # 4. 如果沒有標題正在作用 (current_title is None)，代表這是法條原文的內容 (如：一、道路...)
        # 根據需求「捨棄法條原文部分」，這裡不做任何動作，直接跳過

    # 迴圈結束後，儲存最後一筆
    save_current_block()

    return parsed_data


def generate_markdown(data_list):
    md_output = ""
    for idx, item in enumerate(data_list):
        # 構建 Markdown 區塊
        block = f"""### {item['title']}
**元數據**：{item['meta']}
**內容**：
> {item['content']}
"""
        # 加入 Dify 需要的分隔線 (最後一筆不加，或依需求調整)
        if idx < len(data_list) - 1:
            block += "\n---\n"

        md_output += block
    return md_output


with open('../law2.txt', 'r', encoding="utf-8") as f:
    raw_text = f.read()

# 執行轉換
parsed_list = convert_interpretations_to_md(raw_text)
markdown_result = generate_markdown(parsed_list)

with open("interpretations.md", "w", encoding="utf-8") as f:
    f.write(markdown_result)