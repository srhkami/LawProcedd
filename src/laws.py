import json
from requests import request
from bs4 import BeautifulSoup
from .gemini import call_gemini_api
from .save_markdown import save_markdown


class CleanArticle:
    def __init__(self, part, chapter, section, article, text):
        self.part = part
        self.chapter = chapter
        self.section = section
        self.article = article
        self.text = text

    def to_dict(self):
        return {
            'part': self.part,
            'chapter': self.chapter,
            'section': self.section,
            'article': self.article,
            'text': self.text
        }


class CleanLaw:
    def __init__(self, law_name: str, law_class: str, law_category: str, law_versio: str,
                 law_content: list[CleanArticle]):
        self.name = law_name
        self.hierarchy = law_class  # 層級
        self.category = law_category
        self.version = law_versio
        self.content = law_content

    def to_dict(self):
        return {
            'law_name': self.name,
            'law_hierarchy': self.hierarchy,
            'law_category': self.category,
            'law_version': self.version,
            'law_content': self.content
        }


def pigeon_law_clean(law_id) -> CleanLaw:
    """
    將鴿手資料庫中的法條進行預先處理
    :param law_id: 資料ID
    :return: 直接儲存成JSON
    """
    res = request(method="GET", url=f"http://127.0.0.1:8000/police/police_law/{law_id}/")
    law_obj = res.json()

    raw_data = law_obj['content']  # 你的原始資料
    processed_list: list[CleanArticle] = []  # 已處理的清單
    current_part: str = ""  # 編
    current_chapter: str = ""  # 章
    current_section: str = ""  # 節

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
        clean_article = CleanArticle(
            part=current_part,
            chapter=current_chapter,
            section=current_section,
            article=article,
            text=clean_text
        )
        processed_list.append(clean_article)

    law = CleanLaw(
        law_name=law_obj['law_name'],
        law_class=law_obj['law_class'],
        law_category=law_obj['cate_name'],
        law_versio=law_obj['release_date'],
        law_content=processed_list,
    )

    return law


def traffic_law_clean(law_name) -> CleanLaw:
    """
    todo: 尚未完成修改
    將資料庫的交通法規進行預先處理
    :param law_name: 法規簡稱
    :return: 直接儲存成JSON
    """
    res = request(method="GET", url=f"http://127.0.0.1:8000/traffic/{law_name}/?ordering=id")
    raw_data = res.json().get('results')

    processed_list: list[CleanArticle] = []  # 已處理的清單
    current_part: str = ""  # 編
    current_chapter: str = ""  # 章
    current_section: str = ""  # 節

    for item in raw_data:
        article = item['article'].strip()
        title = item['title'].strip()
        if article == '-1' or article == '-2':
            continue
        if article == '0':
            # 處理篇章節的特例
            if '編' in title:
                current_part = title
            elif '章' in title:
                current_chapter = title
            elif '節' in title:
                current_section = title
            continue

        # 清洗文本
        html_content = item['content']
        soup = BeautifulSoup(html_content, 'html.parser')
        clean_text = soup.get_text()

        clean_article = CleanArticle(
            part=current_part,
            chapter=current_chapter,
            section=current_section,
            article=article,
            text=clean_text
        )
        processed_list.append(clean_article)

    # todo: 此處尚未完成修改
    law_name = '道路交通標誌標線號誌設置規則'  # 法規名稱
    law_class = '法規命令'  # 法規層級
    category_name = '交通'  # 法規類別
    version = '114.06.30'  # 法規版本（修正日期）

    law = CleanLaw(
        law_name=law_name,
        law_class=law_class,
        law_category=category_name,
        law_versio=version,
        law_content=processed_list,
    )

    return law


def law_process_by_gemini(law: CleanLaw) -> None:
    """
    將法規交給Gemini預處理
    """
    for article in law.content:
        data = {
            'law_name': law.name,
            'law_version': law.version,
            'article': article.article,
            'text': article.text,
        }
        message = json.dumps(data, ensure_ascii=False)
        res_text = call_gemini_api(message)
        markdown = res_text
        markdown += '\n---\n'
        save_markdown(
            file_name=f'{law.name}.md',
            text=markdown,
        )
        print(f'{article.article} 已完成')
