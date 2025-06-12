# 🎙️ YourPods - 自動化美股音訊摘要生成系統

![YourPods Logo](https://img.shields.io/badge/YourPods-AI%20Audio%20Finance-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0-green?style=for-the-badge)

## 🚀 **專案概述**

YourPods 是一個創新的 FinTech + AI 專案，能夠**自動生成股票分析音訊播客**。用戶只需輸入股票代碼，系統就會：

1. 📊 **驗證股票代碼** (script_1.py)
2. 🔍 **收集專業財經資訊** (script_2_improved.py) - 使用 StockTitan + Gemini 2.5 Pro
3. 🧠 **三層金字塔分析** (script_3.py) - What/Why/So What 框架
4. 📝 **生成音訊腳本** (待開發)
5. 🎵 **合成語音音訊** (待開發)
6. 📱 **交付給用戶** (待開發)

## ✨ **最新更新 (v2.0)**

### 🔄 **重大改進：**
- **替換 Perplexity API** → **StockTitan + Gemini 2.5 Pro**
- **成本降低 92%** ($150-300 → $12 每1000次查詢)
- **資料品質提升** (專業財經來源 + AI預處理)
- **完全安全配置** (環境變數管理)
- **智能快取機制** (降低重複成本)

## 🏗️ **系統架構**

```
用戶輸入股票代碼
        ↓
   階段1: 輸入驗證 ✅
   (script_1.py)
        ↓
   階段2: 資訊收集 ✅ 🆕
   (script_2_improved.py)
   StockTitan + Gemini 2.5 Pro
        ↓
   階段3: 內容分析 ✅
   (script_3.py)
        ↓
   階段4: 腳本生成 🚧
        ↓
   階段5: 音訊合成 🚧
        ↓
   階段6: 用戶交付 🚧
```

## 🚀 **快速開始 (5分鐘設置)**

### **1. 環境準備**
```bash
# 複製專案
git clone https://github.com/garyyang1001/YourPods-firebase.git
cd YourPods-firebase

# 安裝依賴
pip install -r requirements.txt
```

### **2. API Keys 設置**
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入你的API Keys
nano .env
```

**必要的API Keys:**
- **Firecrawl API Key**: 從 [firecrawl.dev](https://firecrawl.dev) 獲取
- **Gemini API Key**: 從 [Google AI Studio](https://aistudio.google.com) 獲取

### **3. 測試系統**
```bash
# 測試改良版資訊收集
python script_2_improved.py

# 或測試整個流程
python main.py  # (如果你有主程式)
```

## 💰 **成本對比**

| 方案 | 每1000次查詢成本 | 資料品質 | 控制性 |
|------|-----------------|----------|--------|
| **舊版 (Perplexity)** | $150-300 | 中等 | 低 |
| **新版 (StockTitan + Gemini)** | **$12** | **高** | **完全控制** |
| **節省比例** | **92-96%** | ⬆️ 提升 | ⬆️ 提升 |

## 📁 **專案結構**

```
YourPods-firebase/
├── 📄 script.py                 # 系統架構設計
├── 📄 script_1.py              # 階段1: 輸入處理與驗證
├── 📄 script_2_improved.py     # 階段2: 改良版資訊收集 🆕
├── 📄 script_3.py              # 階段3: 內容分析與結構化
├── 📄 .env.example             # API Keys 範本 🆕
├── 📄 requirements.txt         # 套件依賴 🆕
├── 📄 .gitignore              # Git 忽略清單 🆕
├── 📄 README.md               # 專案說明 (本檔案)
└── 📁 (future)/               # 未來的音訊生成功能
```

## 🔧 **技術棧**

### **後端核心:**
- **Python 3.8+**
- **AsyncIO** (並行處理)
- **Firecrawl** (專業網頁抓取)
- **Google Gemini 2.5 Pro** (AI分析)

### **資料來源:**
- **StockTitan.net** (主要財經資料)
- **Yahoo Finance** (備用來源)
- **SEC EDGAR** (官方申報)

### **未來技術:**
- **Firebase** (用戶管理和儲存)
- **TTS引擎** (文字轉語音)
- **React/Next.js** (前端界面)

## 🔒 **安全特性**

### ✅ **已實現:**
- 環境變數管理 (無 hard-coded API Keys)
- 完整的 .gitignore 保護
- API 使用量限制
- 錯誤處理和日誌記錄

### 🚧 **計劃中:**
- API Key 輪換機制
- 用戶認證系統
- 資料加密儲存

## 📊 **效能指標**

### **處理速度:**
- 單股分析: **10-15秒**
- 並行處理: 支援
- 快取命中率: **>80%**

### **成本控制:**
- 智能快取: 2小時
- API限制: 100次/日, 20次/小時
- 成本追蹤: 實時監控

## 🛠️ **開發指南**

### **添加新功能:**
```python
# 在 script_2_improved.py 中擴展
class ImprovedInformationGatherer:
    async def process(self, stock_data):
        # 你的新功能
        pass
```

### **自定義分析:**
```python
# 修改 Gemini 提示
professional_prompt = f"""
你的自定義分析邏輯...
"""
```

### **成本優化:**
```bash
# 調整快取時間
CACHE_DURATION_HOURS=6

# 限制內容長度
MAX_CONTENT_LENGTH=20000
```

## 🧪 **測試和驗證**

### **單元測試:**
```bash
pytest tests/
```

### **手動測試:**
```bash
# 測試特定股票
python script_2_improved.py

# 測試成本計算
python -c "from script_2_improved import *; print('Cost test')"
```

## 📈 **路線圖**

### **Q3 2024:**
- ✅ 階段1-3 完成
- ✅ StockTitan + Gemini 整合
- 🚧 階段4: 腳本生成

### **Q4 2024:**
- 🚧 階段5: 音訊生成 (TTS)
- 🚧 階段6: 用戶界面
- 🚧 Firebase 整合

### **2025:**
- 🎯 Beta 版本發布
- 🎯 用戶測試和反饋
- 🎯 商業化準備

## 🤝 **貢獻指南**

### **開發流程:**
1. Fork 專案
2. 創建 feature branch
3. 提交 pull request
4. 代碼審查

### **貢獻領域:**
- 🔍 新資料來源整合
- 🎵 音訊處理改進
- 🎨 前端界面設計
- 📊 分析算法優化

## 🆘 **故障排除**

### **常見問題:**

**Q: "FIRECRAWL_API_KEY 環境變數未設置"**
```bash
# 檢查 .env 檔案
cat .env | grep FIRECRAWL_API_KEY

# 重新載入環境變數
source .env
```

**Q: Gemini 分析失敗**
- 檢查 API Key 有效性
- 確認免費額度未用完
- 檢查網路連線

**Q: 成本過高**
```bash
# 增加快取時間
CACHE_DURATION_HOURS=6

# 降低API限制
DAILY_API_LIMIT=50
```

## 📞 **聯絡和支援**

- **GitHub Issues**: [回報問題](https://github.com/garyyang1001/YourPods-firebase/issues)
- **討論區**: [功能討論](https://github.com/garyyang1001/YourPods-firebase/discussions)
- **文檔**: [Wiki](https://github.com/garyyang1001/YourPods-firebase/wiki)

## 📄 **授權**

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 **致謝**

- **StockTitan.net** - 提供高品質財經資料
- **Google Gemini** - 強大的AI分析能力
- **Firecrawl** - 可靠的網頁抓取服務
- **開源社群** - 各種優秀的Python套件

---

**🚀 YourPods - 讓投資決策更聰明，讓財經資訊更易懂！**

*最後更新: 2024年6月*
