# 階段1: 輸入處理與驗證階段 (Input Processing)
input_processing_instructions = {
    "name": "輸入處理與驗證階段 (Input Processing)",
    "description": "此階段負責接收用戶輸入的股票代碼，進行格式和有效性驗證，並為後續階段準備必要的基礎資訊。",
    
    "system_prompt": '''
    你是一個專業的金融數據處理助手。你的工作是驗證輸入的股票代碼，並確保它是有效且符合標準格式的。
    
    請遵循以下步驟：
    1. 檢查輸入的股票代碼格式是否正確（如: AAPL, MSFT）
    2. 如果代碼不完整，嘗試進行標準化（如將 'apple' 轉換為 'AAPL'）
    3. 確認該代碼在美國主要交易所（NYSE, NASDAQ）是否存在
    4. 檢查當前是否為美國市場的交易時間
    5. 提供該股票的基本資訊（公司全名、所屬行業、交易所）
    
    你的輸出應該是JSON格式，包含以下欄位：
    {
        "status": "valid" 或 "invalid",
        "standardized_ticker": "標準化的股票代碼",
        "company_name": "公司全名",
        "exchange": "交易所名稱",
        "industry": "所屬行業",
        "market_status": "open" 或 "closed",
        "error_message": "如果無效，說明原因"
    }
    ''',
    
    "user_prompt_template": '''
    請驗證並標準化以下股票代碼：{user_input}
    如果可能，提供該公司的基本資訊。
    ''',
    
    "example_inputs": [
        "AAPL",
        "nvidia",
        "tsla",
        "BRK.A",
        "JPM"
    ],
    
    "validation_rules": [
        "股票代碼必須是有效的字母組合，可包含點號(.)，不超過5個字符",
        "須能映射到實際交易的股票",
        "須提供市場狀態資訊（開市/休市）",
        "須處理常見的股票縮寫或公司名稱"
    ],
    
    "error_handling": {
        "invalid_format": "提示用戶提供正確格式的股票代碼",
        "unknown_ticker": "建議可能的相似股票代碼",
        "api_failure": "記錄錯誤並提供友好的錯誤訊息",
        "retry_strategy": "最多嘗試3次，間隔1秒"
    },
    
    "technical_implementation": {
        "function_name": "process_stock_ticker",
        "dependencies": ["yfinance", "datetime", "pytz"],
        "cache_strategy": "快取已驗證的股票代碼，有效期24小時",
        "async": True
    }
}

# 將階段1的指令轉為實際Python代碼框架
input_processing_code = '''
import yfinance as yf
import datetime
import pytz
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('stock_audio_pipeline')

class InputProcessor:
    """輸入處理與驗證階段的處理器"""
    
    def __init__(self, cache_duration: int = 86400):
        """初始化處理器
        
        Args:
            cache_duration: 快取有效期（秒），預設24小時
        """
        self.cache = {}  # 快取已驗證的股票
        self.cache_duration = cache_duration
        logger.info("InputProcessor initialized")
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """處理用戶輸入的股票代碼
        
        Args:
            user_input: 用戶輸入的原始股票代碼或公司名稱
        
        Returns:
            包含驗證結果和股票資訊的字典
        """
        logger.info(f"Processing user input: {user_input}")
        
        # 1. 清理和標準化輸入
        ticker = self._standardize_input(user_input)
        
        # 2. 檢查快取
        cached_result = self._check_cache(ticker)
        if cached_result:
            logger.info(f"Cache hit for ticker: {ticker}")
            return cached_result
        
        # 3. 驗證股票代碼
        try:
            result = await self._validate_ticker(ticker)
            
            # 4. 更新快取
            if result["status"] == "valid":
                self._update_cache(ticker, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing ticker {ticker}: {str(e)}")
            return {
                "status": "invalid",
                "standardized_ticker": ticker,
                "error_message": f"處理過程中發生錯誤: {str(e)}"
            }
    
    def _standardize_input(self, user_input: str) -> str:
        """標準化用戶輸入
        
        Args:
            user_input: 原始輸入
            
        Returns:
            標準化後的股票代碼
        """
        # 移除空格並轉為大寫
        cleaned = user_input.strip().upper()
        
        # 處理常見公司名稱到股票代碼的映射
        company_to_ticker = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "NVIDIA": "NVDA",
            "FACEBOOK": "META",
            "META": "META",
            "NETFLIX": "NFLX",
            "BERKSHIRE": "BRK-B",
            "BERKSHIRE HATHAWAY": "BRK-B",
            "JP MORGAN": "JPM",
            "JPMORGAN": "JPM"
        }
        
        return company_to_ticker.get(cleaned, cleaned)
    
    def _check_cache(self, ticker: str) -> Optional[Dict[str, Any]]:
        """檢查股票是否在快取中且未過期
        
        Args:
            ticker: 股票代碼
            
        Returns:
            快取的結果或None
        """
        if ticker in self.cache:
            cached_time, cached_data = self.cache[ticker]
            now = datetime.datetime.now().timestamp()
            
            if now - cached_time < self.cache_duration:
                return cached_data
                
        return None
    
    def _update_cache(self, ticker: str, data: Dict[str, Any]) -> None:
        """更新股票資訊快取
        
        Args:
            ticker: 股票代碼
            data: 要快取的資料
        """
        self.cache[ticker] = (datetime.datetime.now().timestamp(), data)
    
    async def _validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """驗證股票代碼並獲取基本資訊
        
        Args:
            ticker: 股票代碼
            
        Returns:
            包含驗證結果和股票資訊的字典
        """
        try:
            # 使用yfinance獲取股票資訊
            stock_info = yf.Ticker(ticker).info
            
            # 檢查是否找到有效股票
            if 'regularMarketPrice' not in stock_info or stock_info['regularMarketPrice'] is None:
                return {
                    "status": "invalid",
                    "standardized_ticker": ticker,
                    "error_message": "找不到此股票代碼的市場資訊"
                }
            
            # 檢查市場狀態
            market_status = self._check_market_status()
            
            return {
                "status": "valid",
                "standardized_ticker": ticker,
                "company_name": stock_info.get('longName', '未知'),
                "exchange": stock_info.get('exchange', '未知'),
                "industry": stock_info.get('industry', '未知'),
                "market_status": market_status,
                "current_price": stock_info.get('regularMarketPrice', 0),
                "currency": stock_info.get('currency', 'USD')
            }
            
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {str(e)}")
            return {
                "status": "invalid",
                "standardized_ticker": ticker,
                "error_message": f"無法驗證股票代碼: {str(e)}"
            }
    
    def _check_market_status(self) -> str:
        """檢查美國市場是否開市
        
        Returns:
            'open' 或 'closed'
        """
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        
        # 判斷是否為交易日 (週一到週五)
        if now.weekday() >= 5:  # 0=週一, 5=週六, 6=週日
            return "closed"
        
        # 判斷是否在交易時間 (9:30 - 16:00 東部時間)
        market_open = now.replace(hour=9, minute=30, second=0)
        market_close = now.replace(hour=16, minute=0, second=0)
        
        if market_open <= now <= market_close:
            return "open"
        else:
            return "closed"
'''

print("階段1: 輸入處理與驗證階段 (Input Processing) 指令設計完成")
print(f"系統提示詞包含 {len(input_processing_instructions['system_prompt'])} 個字符")
print(f"已設計 {len(input_processing_instructions['validation_rules'])} 條驗證規則")
print(f"已提供 {len(input_processing_instructions['example_inputs'])} 個範例輸入")
print(f"技術實現框架代碼共 {len(input_processing_code.split('\n'))} 行")