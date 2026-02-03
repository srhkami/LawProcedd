import json
from requests import request
from src.laws import pigeon_law_clean, law_process_by_gemini

id_list = [76, 77, 78, 79, 80, 81, 82, 84, 86, 87, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103,
           104, 105, 106, 107, 108, 109, 110, 111, 112, ]

if __name__ == "__main__":
    """
    用來給法規資料庫的條款進行預處理
    將每個條都加入編章節以增加關聯性
    """
    for id in id_list:
        law = pigeon_law_clean(id)
        print(f'---開始執行{law.name}---')
        law_process_by_gemini(law)
        print('✅ 執行完畢')
