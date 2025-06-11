# 創建多階段自動化流程的完整指令集

instruction_set = {
    "system_architecture": {
        "overview": "基於Perplexity API的美股音訊摘要生成系統",
        "design_philosophy": "將複雜任務拆分為獨立、可測試的階段，每個階段負責特定功能",
        "key_principles": [
            "單一職責原則 - 每個階段只做一件事",
            "可觀測性 - 每個階段都有清晰的輸入輸出日誌",
            "容錯設計 - 失敗時能夠優雅處理並提供反饋",
            "可擴展性 - 新增功能時無需重構核心邏輯"
        ]
    },
    
    "stage_breakdown": {
        "stage_1": {
            "name": "輸入處理與驗證階段 (Input Processing)",
            "responsibility": "接收並驗證股票代碼，進行基本的格式檢查",
            "input": "原始股票代碼 (如: 'NVDA', 'AAPL')",
            "output": "標準化的股票代碼和基本資訊",
            "key_functions": [
                "代碼格式驗證",
                "市場開盤狀態檢查", 
                "代碼標準化",
                "請求記錄"
            ]
        },
        
        "stage_2": {
            "name": "資訊蒐集階段 (Information Gathering)",
            "responsibility": "使用Perplexity API收集相關的財經資訊",
            "input": "標準化股票代碼",
            "output": "結構化的原始資訊數據",
            "key_functions": [
                "構建搜索查詢",
                "呼叫Perplexity API",
                "資訊來源驗證",
                "原始數據儲存"
            ]
        },
        
        "stage_3": {
            "name": "內容分析與結構化階段 (Content Analysis)",
            "responsibility": "將原始資訊按照三層金字塔框架進行分析和組織",
            "input": "原始財經資訊",
            "output": "結構化的分析內容 (What/Why/So What)",
            "key_functions": [
                "事實提取 (What)",
                "背景分析 (Why)",
                "洞見生成 (So What)",
                "內容品質評估"
            ]
        },
        
        "stage_4": {
            "name": "腳本生成階段 (Script Generation)",
            "responsibility": "將結構化內容轉換成適合語音播報的腳本",
            "input": "結構化分析內容",
            "output": "5分鐘音訊腳本",
            "key_functions": [
                "內容編排",
                "語氣調整",
                "時間控制",
                "過渡語句添加"
            ]
        },
        
        "stage_5": {
            "name": "音訊生成階段 (Audio Generation)",
            "responsibility": "將腳本轉換成高品質音訊文件",
            "input": "最終腳本",
            "output": "MP3音訊文件",
            "key_functions": [
                "TTS API調用",
                "音訊品質控制",
                "文件格式處理",
                "音訊後處理"
            ]
        },
        
        "stage_6": {
            "name": "交付與反饋階段 (Delivery & Feedback)",
            "responsibility": "將最終產品交付給用戶並收集反饋",
            "input": "音訊文件",
            "output": "用戶可訪問的音訊連結",
            "key_functions": [
                "文件上傳",
                "連結生成",
                "交付通知",
                "反饋收集"
            ]
        }
    }
}

print("多階段自動化流程架構設計完成")
print(f"總共包含 {len(instruction_set['stage_breakdown'])} 個主要階段")