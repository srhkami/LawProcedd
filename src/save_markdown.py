import os


def save_markdown(file_name: str, text: str, is_cover: bool = False) -> None:
    save_path = os.path.join("D:\Coding\Python\law-process\md", file_name)
    # 如果是覆蓋模式，刪除舊檔
    if is_cover and os.path.exists(save_path):
        os.remove(save_path)
    try:
        with open(save_path, "a", encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        print(e)
