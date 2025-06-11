# 階段2: 資訊蒐集階段 (Information Gathering)
information_gathering_instructions = {
    "name": "資訊蒐集階段 (Information Gathering)",
    "description": "此階段負責使用Perplexity API收集與股票相關的即時財經資訊，為後續的內容分析提供原料。",
    
    "system_prompt": '''
    你是一個專業的財經資訊研究助手，擅長搜索和收集關於特定股票的最新、準確且相關的資訊。
    
    你的搜索策略應該包含：
    1. 即時股價表現和交易數據
    2. 最新的公司公告和新聞
    3. 分析師評級和研究報告
    4. 行業動態和競爭情況
    5. 宏觀經濟影響因素
    
    搜索來源優先順序：
    1. 官方公司公告（SEC filings, 財報, 投資者關係）
    2. 主要財經媒體（Bloomberg, Reuters, CNBC, Wall Street Journal）
    3. 專業分析機構報告（Goldman Sachs, Morgan Stanley等）
    4. 行業相關新聞和數據
    
    請確保收集的資訊：
    - 時效性：優先收集最近24-48小時的資訊
    - 權威性：來自可信的財經來源
    - 相關性：與該股票直接相關
    - 完整性：涵蓋股價、基本面、技術面各個維度
    
    你的輸出應該包含：
    - 收集到的原始資訊
    - 資訊來源和時間戳
    - 資訊的重要性評估
    - 潛在的關鍵驅動因素識別
    ''',
    
    "user_prompt_template": '''
    請搜索並收集關於股票 {standardized_ticker} ({company_name}) 的最新財經資訊。
    
    請特別關注：
    1. 今日股價表現和成交量變化
    2. 最近的公司重大公告或新聞
    3. 分析師的最新評級或價格目標變動
    4. 該公司所屬行業 ({industry}) 的相關動態
    5. 可能影響股價的宏觀因素
    
    當前市場狀態：{market_status}
    當前股價：${current_price} {currency}
    
    請提供詳細、準確且即時的資訊，並註明每個資訊點的來源。
    ''',
    
    "perplexity_api_config": {
        "model": "sonar-pro",
        "temperature": 0.2,  # 較低的溫度確保更準確的事實
        "max_tokens": 2000,
        "search_recency_filter": "day",  # 優先搜索最近一天的資訊
        "include_citations": True,
        "search_domain_filter": [
            "sec.gov",
            "investor.com", 
            "bloomberg.com",
            "reuters.com",
            "cnbc.com",
            "wsj.com",
            "yahoo.com/finance",
            "marketwatch.com",
            "fool.com"
        ]
    },
    
    "search_strategy": {
        "primary_queries": [
            "{ticker} stock price today news",
            "{ticker} latest earnings financial report",
            "{ticker} analyst rating price target",
            "{ticker} {company_name} breaking news",
            "{ticker} quarterly results guidance"
        ],
        "secondary_queries": [
            "{industry} sector news today",
            "{ticker} vs competitors comparison",
            "{ticker} institutional investor holdings",
            "{ticker} technical analysis support resistance"
        ],
        "fallback_queries": [
            "{company_name} stock analysis",
            "{ticker} financial performance",
            "{industry} market outlook"
        ]
    },
    
    "information_categories": {
        "price_action": {
            "description": "股價相關資訊",
            "keywords": ["price", "volume", "trading", "high", "low", "change", "percentage"]
        },
        "fundamental_news": {
            "description": "基本面新聞",
            "keywords": ["earnings", "revenue", "profit", "guidance", "financial", "report"]
        },
        "analyst_coverage": {
            "description": "分析師覆蓋",
            "keywords": ["analyst", "rating", "target", "upgrade", "downgrade", "recommendation"]
        },
        "corporate_actions": {
            "description": "公司行動",
            "keywords": ["merger", "acquisition", "dividend", "split", "buyback", "announcement"]
        },
        "industry_context": {
            "description": "行業背景",
            "keywords": ["sector", "industry", "competition", "market share", "trends"]
        }
    },
    
    "quality_metrics": {
        "source_credibility": "評估資訊來源的可信度（1-10分）",
        "information_freshness": "資訊的新鮮度（小時數）",
        "relevance_score": "與目標股票的相關性（1-10分）",
        "actionability": "資訊的可操作性（1-10分）"
    },
    
    "error_handling": {
        "no_recent_news": "如果沒有最新新聞，搜索較長時間範圍的重要資訊",
        "api_rate_limit": "實施指數退避重試策略",
        "low_quality_results": "調整搜索關鍵字並重新搜索",
        "timeout": "切換到備用API或搜索策略"
    },
    
    "output_structure": {
        "raw_information": "從API獲取的原始文字資訊",
        "structured_data": {
            "price_data": "股價相關數據",
            "news_events": "重要新聞事件列表",
            "analyst_opinions": "分析師觀點摘要",
            "market_context": "市場環境資訊"
        },
        "information_sources": "所有資訊來源的詳細引用",
        "collection_metadata": {
            "timestamp": "資訊收集時間",
            "api_calls_made": "API調用次數",
            "search_queries_used": "使用的搜索查詢",
            "quality_assessment": "整體資訊品質評估"
        }
    }
}

# 實際的Perplexity API調用代碼框架
information_gathering_code = '''
import requests
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('information_gathering')

class InformationGatherer:
    """資訊蒐集階段的處理器"""
    
    def __init__(self, api_key: str, max_retries: int = 3, retry_delay: float = 1.0):
        """初始化資訊收集器
        
        Args:
            api_key: Perplexity API密鑰
            max_retries: 最大重試次數
            retry_delay: 重試延遲時間（秒）
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.search_budget = {"calls_made": 0, "daily_limit": 100}
        logger.info("InformationGatherer initialized")
    
    async def process(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """收集股票相關資訊
        
        Args:
            stock_data: 來自階段1的股票資料
            
        Returns:
            收集到的資訊數據
        """
        logger.info(f"Starting information gathering for {stock_data['standardized_ticker']}")
        
        ticker = stock_data['standardized_ticker']
        company_name = stock_data.get('company_name', '')
        industry = stock_data.get('industry', '')
        
        # 1. 準備搜索查詢
        search_queries = self._prepare_search_queries(ticker, company_name, industry)
        
        # 2. 執行並行搜索
        try:
            search_results = await self._execute_parallel_searches(search_queries)
            
            # 3. 整理和結構化資訊
            structured_info = self._structure_information(search_results)
            
            # 4. 品質評估
            quality_score = self._assess_information_quality(structured_info)
            
            return {
                "status": "success",
                "ticker": ticker,
                "raw_information": search_results,
                "structured_data": structured_info,
                "quality_score": quality_score,
                "collection_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "api_calls_made": len(search_queries),
                    "search_queries_used": search_queries,
                    "processing_time": time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error gathering information for {ticker}: {str(e)}")
            return {
                "status": "error",
                "ticker": ticker,
                "error_message": str(e),
                "partial_data": None
            }
    
    def _prepare_search_queries(self, ticker: str, company_name: str, industry: str) -> List[str]:
        """準備針對性的搜索查詢
        
        Args:
            ticker: 股票代碼
            company_name: 公司名稱
            industry: 行業分類
            
        Returns:
            搜索查詢列表
        """
        # 主要查詢 - 聚焦於最重要的資訊
        primary_queries = [
            f"{ticker} stock price today trading volume news latest",
            f"{ticker} {company_name} quarterly earnings results guidance",
            f"{ticker} analyst rating price target upgrade downgrade",
            f"{ticker} latest news announcements SEC filings",
            f"{industry} sector performance {ticker} comparison"
        ]
        
        # 如果是市場開盤時間，增加即時性查詢
        if self._is_market_hours():
            primary_queries.extend([
                f"{ticker} intraday trading unusual volume spike",
                f"{ticker} real-time news catalyst price movement"
            ])
        
        return primary_queries[:6]  # 限制查詢數量以控制成本
    
    async def _execute_parallel_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """並行執行多個搜索查詢
        
        Args:
            queries: 搜索查詢列表
            
        Returns:
            搜索結果列表
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self._single_search(session, query) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        # 過濾掉失敗的請求
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Query {i} failed: {str(result)}")
            else:
                valid_results.append(result)
                
        return valid_results
    
    async def _single_search(self, session: aiohttp.ClientSession, query: str) -> Dict[str, Any]:
        """執行單個搜索查詢
        
        Args:
            session: HTTP會話
            query: 搜索查詢
            
        Returns:
            搜索結果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise financial information researcher. Provide current, accurate financial data with proper citations."
                },
                {
                    "role": "user", 
                    "content": query
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
            "search_recency_filter": "day",
            "return_citations": True
        }
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.search_budget["calls_made"] += 1
                        return {
                            "query": query,
                            "response": result,
                            "timestamp": datetime.now().isoformat(),
                            "success": True
                        }
                    else:
                        logger.warning(f"API request failed with status {response.status}")
                        
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for query '{query}': {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 指數退避
                    
        return {
            "query": query,
            "response": None,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": "Max retries exceeded"
        }
    
    def _structure_information(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """將原始搜索結果結構化
        
        Args:
            search_results: 原始搜索結果
            
        Returns:
            結構化的資訊
        """
        structured = {
            "price_data": [],
            "news_events": [],
            "analyst_opinions": [],
            "market_context": [],
            "company_fundamentals": []
        }
        
        # 這裡需要實現具體的資訊分類邏輯
        # 暫時返回基本結構
        for result in search_results:
            if result["success"] and result["response"]:
                content = result["response"].get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 根據關鍵字分類資訊
                if any(keyword in content.lower() for keyword in ["price", "trading", "volume"]):
                    structured["price_data"].append({
                        "content": content,
                        "source": result["query"],
                        "timestamp": result["timestamp"]
                    })
                    
                if any(keyword in content.lower() for keyword in ["analyst", "rating", "target"]):
                    structured["analyst_opinions"].append({
                        "content": content,
                        "source": result["query"],
                        "timestamp": result["timestamp"]
                    })
                
                # 其他分類邏輯...
                
        return structured
    
    def _assess_information_quality(self, structured_info: Dict[str, Any]) -> Dict[str, float]:
        """評估收集資訊的品質
        
        Args:
            structured_info: 結構化資訊
            
        Returns:
            品質評估分數
        """
        # 計算各個維度的評分
        completeness = min(1.0, len(structured_info["price_data"]) * 0.3 + 
                          len(structured_info["analyst_opinions"]) * 0.4 +
                          len(structured_info["news_events"]) * 0.3)
        
        timeliness = 1.0  # 需要根據資訊時間戳計算
        
        return {
            "overall_score": (completeness + timeliness) / 2,
            "completeness": completeness,
            "timeliness": timeliness,
            "source_diversity": min(1.0, len(structured_info) / 5)
        }
    
    def _is_market_hours(self) -> bool:
        """檢查是否為市場交易時間"""
        # 簡化實現 - 實際應該考慮美國東部時間
        now = datetime.now()
        return 9 <= now.hour <= 16 and now.weekday() < 5
'''

print("階段2: 資訊蒐集階段 (Information Gathering) 指令設計完成")
print(f"Perplexity API配置包含 {len(information_gathering_instructions['perplexity_api_config'])} 個參數")
print(f"搜索策略包含 {len(information_gathering_instructions['search_strategy']['primary_queries'])} 個主要查詢")
print(f"資訊分類包含 {len(information_gathering_instructions['information_categories'])} 個類別")
print(f"技術實現框架代碼共 {len(information_gathering_code.split('\n'))} 行")