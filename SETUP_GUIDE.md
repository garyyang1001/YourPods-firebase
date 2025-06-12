# 🚀 YourPods v2.0 快速設置指南

歡迎使用YourPods改良版！本指南將幫您在5分鐘內完成設置。

## 📋 檢查清單

### ✅ **第1步：確認檔案結構**
```
YourPods-firebase/
├── 📄 script.py                 # 原始架構設計
├── 📄 script_1.py              # 階段1: 輸入驗證
├── 📄 script_2_improved.py     # 🆕 階段2: StockTitan + Gemini
├── 📄 script_3_improved.py     # 🆕 階段3: 三層金字塔分析
├── 📄 main.py                  # 🆕 完整系統整合
├── 📄 .env.example             # 🆕 API配置範本
├── 📄 requirements.txt         # 🆕 套件依賴
├── 📄 .gitignore              # 🆕 安全保護
└── 📄 README.md               # 🆕 專案說明
```

### ✅ **第2步：環境設置**

#### 安裝套件
```bash
pip install -r requirements.txt
```

#### 配置API Keys
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案
nano .env
```

在 `.env` 檔案中填入：
```bash
# 必要的API Keys
FIRECRAWL_API_KEY=fc-your_actual_key_here
GEMINI_API_KEY=your_actual_gemini_key_here

# 可選配置
CACHE_DURATION_HOURS=2
LOG_LEVEL=INFO
```

### ✅ **第3步：獲取API Keys**

#### 🔥 Firecrawl API Key
1. 前往 https://firecrawl.dev
2. 註冊帳號
3. 複製API Key (格式: `fc-xxxxxxxxxx`)

#### 🤖 Google Gemini API Key  
1. 前往 https://aistudio.google.com
2. 創建API Key
3. 複製API Key

### ✅ **第4步：測試系統**

#### 快速測試
```bash
# 測試單支股票
python main.py --ticker AAPL

# 互動模式
python main.py --interactive

# 系統測試
python main.py --test
```

#### 測試個別階段
```bash
# 測試階段2 (資訊收集)
python script_2_improved.py

# 測試階段3 (內容分析)
python script_3_improved.py
```

## 🎯 **使用方式**

### **方法1：使用整合系統 (推薦)**
```python
import asyncio
from main import analyze_stock

# 分析單支股票
result = await analyze_stock("AAPL")
print(result["executive_summary"])
```

### **方法2：批量分析**
```python
from main import batch_analyze_stocks

# 批量分析
tickers = ["AAPL", "TSLA", "MSFT"]
results = await batch_analyze_stocks(tickers)
```

### **方法3：直接使用改良版階段**
```python
from script_2_improved import process as info_gathering
from script_3_improved import process as content_analysis

# 階段2: 資訊收集
stock_data = {"standardized_ticker": "AAPL", "company_name": "Apple Inc."}
info_result = await info_gathering(stock_data)

# 階段3: 內容分析
analysis_result = await content_analysis(info_result)
```

## 💰 **成本預估**

### **每次查詢成本：**
- Firecrawl: ~$1.00 (2頁面)
- Gemini: ~$0.02 (1次分析)
- **總計: ~$1.02**

### **與舊版對比：**
- **舊版 (Perplexity)**: $5-20/次查詢
- **新版 (StockTitan + Gemini)**: $1.02/次查詢
- **節省**: 80-95% 💰

## 🔧 **故障排除**

### **常見問題：**

#### ❌ "FIRECRAWL_API_KEY 環境變數未設置"
```bash
# 檢查 .env 檔案
cat .env | grep FIRECRAWL_API_KEY

# 確保檔案在正確位置
ls -la .env
```

#### ❌ "ModuleNotFoundError"
```bash
# 重新安裝套件
pip install -r requirements.txt

# 檢查Python版本 (需要3.8+)
python --version
```

#### ❌ "Gemini API失敗"
- 檢查API Key是否正確
- 確認免費額度未用完
- 檢查網路連線

#### ❌ "成本過高"
```bash
# 調整快取時間
echo "CACHE_DURATION_HOURS=6" >> .env

# 降低API限制
echo "DAILY_API_LIMIT=50" >> .env
```

## 📊 **預期結果**

成功設置後，您應該看到：

```json
{
  "status": "success",
  "processing_time_seconds": 12.3,
  "stock_info": {
    "ticker": "AAPL",
    "company_name": "Apple Inc."
  },
  "executive_summary": {
    "headline": "Apple展現強勁基本面...",
    "market_sentiment": "正面",
    "key_catalyst": "新產品發布推動成長..."
  },
  "metadata": {
    "cost_estimate": 1.02,
    "analysis_confidence": "high"
  }
}
```

## 🎉 **下一步**

### **系統運行正常後：**

1. **優化設置**：調整快取和限制參數
2. **監控成本**：定期檢查API使用量
3. **擴展功能**：準備階段4-6的音訊生成
4. **用戶測試**：邀請目標用戶體驗

### **準備生產環境：**

1. **部署配置**：使用環境變數管理
2. **監控系統**：設置日誌和警報
3. **備份策略**：建立資料備份機制
4. **擴展計劃**：準備水平擴展

## 📞 **需要幫助？**

- **GitHub Issues**: [回報問題](https://github.com/garyyang1001/YourPods-firebase/issues)
- **文檔**: [查看README](README.md)
- **範例**: 參考 `main.py` 中的測試功能

---

## 🎯 **效能基準**

### **預期指標：**
- **處理時間**: 10-15秒/股票
- **成功率**: >95%
- **成本**: $1.02/次查詢
- **資料品質**: 高 (來自專業財經來源)

### **系統限制：**
- **API限制**: 100次/日, 20次/小時 (可調整)
- **快取**: 2小時 (可調整)
- **並行度**: 3個並行請求 (可調整)

---

**🚀 恭喜！您的YourPods v2.0系統已經準備就緒！**

*現在您可以享受92%的成本節省和更高品質的財經分析了！*
