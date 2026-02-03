import os
from google import genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# 初始化新版 Google GenAI Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = 'gemini-3-flash-preview'

# 系統提示詞
SYSTEM_PROMPT = '''
# 指令
將輸入法條轉換為 Dify 專用 Markdown 格式。

# 規則
1. 條號：{{article}}中的文字，遇到中式數字請轉阿拉伯數字（如：七之一 -> 7-1），不要留下空格；若原文無「第 X 條」而僅有「一、」、「二、」，請改為「第X點」。
2. 條文內容：保留{{text}}的內容，款/目需換行縮排。
3. 關聯索引：找出輸入法條中有關的其他法條（包括其他法規），將「前項、第一項」改寫「[法規名稱]第X條第X項」。
4. 檢索摘要：以白話文總結規範重點。
5. 潛在查詢：生成1到10個用戶可能會提問的問題，法條越複雜生成越多。

# 輸出範本
### [條號]
**元數據**:{{law_name}}|{{law_version}}
**條文內容**:
> [完整條文，款目縮排]
**關聯索引**:
* [條號]
**標籤**:
#[關鍵字] #[白話關鍵字]
**檢索摘要**:
[白話總結]
**潛在查詢:
* [問題]

# 輸出限制
僅輸出 Markdown，無開場白。
'''

# 生成參數
generation_config = genai.types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    temperature=0.0,
    max_output_tokens=8192,
    top_p=0.95,
)


# 定義生成函式 (LLM)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception)
)
def call_gemini_api(message: str) -> str:
    """
    呼叫 Gemini API
    """
    try:
        # 新版呼叫方式：client.models.generate_content
        response = client.models.generate_content(
            model=MODEL_ID,
            config=generation_config,
            contents=message
        )
        return response.text
    except Exception as e:
        print(e)
        # 新版 SDK 的錯誤訊息結構可能不同，建議印出來除錯
        raise e
