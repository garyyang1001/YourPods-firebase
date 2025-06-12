# 階段2: 改良版資訊蒐集 - StockTitan + Gemini 2.5 Pro
# 替代原本的 Perplexity API 實現

import asyncio
import json
import logging
import re
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Required packages:
# pip install aiohttp firecrawl-py google-generativeai python-dotenv

import aiohttp
import google.generativeai as genai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('YourPods_InformationGathering')

@dataclass
class YourPodsConfig:
    """YourPods 專案配置 - 安全的API管理"""
    
    def __init__(self):
        # 從環境變數載入API Keys
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.brave_api_key = os.getenv('BRAVE_API_KEY')  # 可選
        
        # 驗證必要的API Keys
        if not self.firecrawl_api_key:
            raise ValueError("❌ FIRECRAWL_API_KEY 環境變數未設置 - 請檢查 .env 檔案")
        
        if not self.gemini_api_key:
            raise ValueError("❌ GEMINI_API_KEY 環境變數未設置 - 請檢查 .env 檔案")
        
        # YourPods 系統配置
        self.stocktitan_base = "https://www.stocktitan.net"
        self.cache_duration_hours = int(os.getenv('CACHE_DURATION_HOURS', '2'))
        self.max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', '30000'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '15000'))
        
        # 成本控制
        self.daily_api_limit = int(os.getenv('DAILY_API_LIMIT', '100'))
        self.hourly_api_limit = int(os.getenv('HOURLY_API_LIMIT', '20'))
        
        logger.info("✅ YourPods配置載入成功 - StockTitan + Gemini 2.5 Pro")

class ImprovedInformationGatherer:
    """改良版資訊蒐集階段 - 完全替代 Perplexity API"""
    
    def __init__(self):
        # 載入配置
        self.config = YourPodsConfig()
        
        # 初始化服務
        self.firecrawl = FirecrawlApp(api_key=self.config.firecrawl_api_key)
        
        # 配置Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 快取和使用量追蹤
        self.cache = {}
        self.api_usage_tracker = {
            'daily_calls': 0,
            'hourly_calls': 0,
            'last_reset_day': datetime.now().day,
            'last_reset_hour': datetime.now().hour
        }
        
        logger.info("🚀 YourPods 改良版資訊收集器初始化完成")
    
    async def process(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主要處理函數 - 與原本 script_2.py 完全相容
        
        Args:
            stock_data: 來自 script_1.py 的股票資料
            
        Returns:
            與原本 script_2.py 相同格式的結果，但使用 StockTitan + Gemini
        """
        ticker = stock_data['standardized_ticker']
        company_name = stock_data.get('company_name', '')
        industry = stock_data.get('industry', '')
        
        logger.info(f"🎯 [YourPods] 開始收集 {ticker} ({company_name}) 的專業財經資訊")
        
        try:
            # 1. 檢查API使用限制
            if not self._check_api_limits():
                return self._create_error_response(ticker, "API使用量已達到每日/每小時限制")
            
            # 2. 檢查快取
            cached_result = self._check_cache(ticker)
            if cached_result:
                logger.info(f"📋 使用快取資料: {ticker}")
                return cached_result
            
            # 3. 抓取 StockTitan 專業資料
            stocktitan_data = await self._fetch_professional_data(ticker, company_name, industry)
            
            # 4. 品質檢查，必要時補充備用來源
            if not self._is_data_sufficient(stocktitan_data):
                logger.info(f"📡 資料不足，啟用備用來源...")
                backup_data = await self._fetch_backup_sources(ticker)
                stocktitan_data.extend(backup_data)
            
            # 5. 使用 Gemini 2.5 Pro 進行專業分析
            gemini_analysis = await self._analyze_with_gemini_pro(ticker, stocktitan_data, industry)
            
            # 6. 結構化輸出 (與原本 script_2.py 格式完全相容)
            result = self._format_compatible_result(ticker, stocktitan_data, gemini_analysis)
            
            # 7. 更新快取和使用量
            self._update_cache(ticker, result)
            self._update_api_usage()
            
            logger.info(f"✅ {ticker} 專業資訊收集完成 - 來源數: {len(stocktitan_data)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ {ticker} 資訊收集失敗: {str(e)}")
            return self._create_error_response(ticker, str(e))
    
    async def _fetch_professional_data(self, ticker: str, company_name: str, industry: str) -> List[Dict[str, Any]]:
        """抓取 StockTitan 的專業財經資料"""
        
        # 構建智能URL策略
        primary_urls = [
            f"{self.config.stocktitan_base}/news/{ticker}/",  # 個股專頁
            f"{self.config.stocktitan_base}/news/today",      # 今日市場新聞
        ]
        
        # 根據市場狀態和時間加入額外來源
        if self._is_market_hours():
            primary_urls.append(f"{self.config.stocktitan_base}/news/live.html")
        
        if self._is_earnings_season():
            primary_urls.append(f"{self.config.stocktitan_base}/news/earnings.html")
        
        # 並行抓取所有來源
        tasks = [self._scrape_stocktitan_url(url, ticker) for url in primary_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾和整理成功結果
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ URL {primary_urls[i]} 抓取失敗: {str(result)}")
            elif result and result.get('success'):
                successful_results.append(result)
        
        logger.info(f"📊 成功抓取 {len(successful_results)}/{len(primary_urls)} 個StockTitan來源")
        return successful_results
    
    async def _scrape_stocktitan_url(self, url: str, ticker: str) -> Dict[str, Any]:
        """抓取單個 StockTitan URL"""
        
        try:
            logger.info(f"🌐 抓取專業財經來源: {url}")
            
            # 使用 Firecrawl 進行專業網頁抓取
            result = self.firecrawl.scrape_url(
                url=url,
                params={
                    'formats': ['markdown'],
                    'onlyMainContent': True,
                    'removeBase64Images': True,
                    'timeout': self.config.request_timeout,
                    'waitFor': 2000  # 等待動態內容載入
                }
            )
            
            if result.get('success'):
                content = result.get('markdown', '')
                
                # 智能提取與目標股票相關的內容
                relevant_content = self._extract_intelligent_content(content, ticker)
                
                if relevant_content:
                    # 提取 StockTitan 的 Rhea-AI 專業分析數據
                    rhea_ai_data = self._extract_rhea_ai_analysis(content)
                    
                    return {
                        'url': url,
                        'source': 'StockTitan_Professional',
                        'raw_content': content,
                        'relevant_content': relevant_content,
                        'rhea_ai_analysis': rhea_ai_data,
                        'timestamp': datetime.now().isoformat(),
                        'success': True,
                        'quality_score': self._calculate_content_quality(relevant_content, rhea_ai_data)
                    }
                else:
                    logger.info(f"📭 {url} 沒有找到 {ticker} 的相關專業內容")
                    return {'url': url, 'success': False, 'reason': 'No relevant professional content'}
            else:
                return {'url': url, 'success': False, 'error': 'Firecrawl抓取失敗'}
                
        except Exception as e:
            logger.error(f"❌ 抓取 {url} 失敗: {str(e)}")
            return {'url': url, 'success': False, 'error': str(e)}
    
    def _extract_intelligent_content(self, content: str, ticker: str) -> str:
        """智能提取與股票相關的內容"""
        
        if not content:
            return ""
        
        # 分割內容為段落和句子
        paragraphs = content.split('\n\n')
        relevant_paragraphs = []
        
        # 多層次搜索模式
        primary_patterns = [
            ticker.upper(),
            ticker.lower(),
            f"({ticker})",
            f"NYSE: {ticker}",
            f"NASDAQ: {ticker}",
            f"${ticker}"
        ]
        
        # 財經相關關鍵字
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'guidance', 'analyst',
            'rating', 'target', 'price', 'volume', 'trading',
            'quarterly', 'annual', 'financial', 'results'
        ]
        
        for paragraph in paragraphs:
            # 檢查是否包含目標股票
            contains_ticker = any(pattern in paragraph for pattern in primary_patterns)
            
            # 檢查是否包含財經關鍵字
            contains_financial = any(keyword in paragraph.lower() for keyword in financial_keywords)
            
            if contains_ticker or (contains_financial and len(paragraph) > 100):
                relevant_paragraphs.append(paragraph.strip())
        
        result = '\n\n'.join(relevant_paragraphs)
        logger.info(f"📝 為 {ticker} 智能提取了 {len(relevant_paragraphs)} 個專業段落")
        
        return result
    
    def _extract_rhea_ai_analysis(self, content: str) -> Dict[str, str]:
        """提取 StockTitan 的 Rhea-AI 專業分析數據"""
        
        rhea_analysis = {
            "summary": "",
            "sentiment": "",
            "impact": "",
            "end_of_day": "",
            "tags": []
        }
        
        # 改良的正則表達式模式
        patterns = {
            "summary": r"Rhea-AI Summary[:\s]*(.*?)(?=\n\n|Rhea-AI|Tags|$)",
            "sentiment": r"Rhea-AI Sentiment[:\s]*(.*?)(?=\n\n|Rhea-AI|Tags|$)",
            "impact": r"Rhea-AI Impact[:\s]*(.*?)(?=\n\n|Rhea-AI|Tags|$)",
            "end_of_day": r"End-of-Day[:\s]*(.*?)(?=\n\n|Rhea-AI|Tags|$)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                rhea_analysis[key] = match.group(1).strip()
        
        # 提取標籤
        tags_match = re.search(r"Tags[:\s]*(.*?)(?=\n\n|$)", content, re.DOTALL | re.IGNORECASE)
        if tags_match:
            tags_text = tags_match.group(1).strip()
            rhea_analysis["tags"] = [tag.strip() for tag in tags_text.split() if tag.strip()]
        
        # 記錄找到的專業AI數據
        found_data = [k for k, v in rhea_analysis.items() if v and k != 'tags']
        if found_data:
            logger.info(f"🤖 找到Rhea-AI專業分析: {', '.join(found_data)}")
        
        return rhea_analysis
    
    async def _fetch_backup_sources(self, ticker: str) -> List[Dict[str, Any]]:
        """備用資料來源"""
        
        backup_sources = [
            f"https://finance.yahoo.com/quote/{ticker}/news/",
            f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
        ]
        
        logger.info(f"🔄 啟用備用財經來源...")
        
        backup_results = []
        for url in backup_sources[:1]:  # 控制成本，只使用1個備用來源
            try:
                result = self.firecrawl.scrape_url(
                    url=url,
                    params={
                        'formats': ['markdown'],
                        'onlyMainContent': True,
                        'timeout': 10000
                    }
                )
                
                if result.get('success'):
                    backup_results.append({
                        'url': url,
                        'source': 'Backup_Financial',
                        'raw_content': result.get('markdown', ''),
                        'relevant_content': self._extract_intelligent_content(result.get('markdown', ''), ticker),
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ 備用來源 {url} 失敗: {str(e)}")
        
        return backup_results
    
    async def _analyze_with_gemini_pro(self, ticker: str, data_sources: List[Dict[str, Any]], industry: str) -> Dict[str, Any]:
        """使用 Gemini 2.5 Pro 進行專業財經分析"""
        
        # 整合所有專業內容
        combined_analysis = self._combine_professional_content(data_sources)
        
        if not combined_analysis.strip():
            return {"error": "沒有足夠的專業內容進行分析", "success": False}
        
        # 構建專業財經分析提示
        professional_prompt = f"""
你是頂級的華爾街財經分析師，專門分析美股市場。請對股票 {ticker} 進行專業分析。

行業背景: {industry}

可用的專業資料:
{combined_analysis}

請提供結構化的專業分析，包括：

## 1. 核心催化劑 (Key Catalyst)
- 識別最重要的價格驅動事件
- 評估事件的重要性和時效性

## 2. 市場情緒分析 (Market Sentiment)
- 投資者反應和情緒指標
- 交易量和價格行為分析

## 3. 基本面評估 (Fundamental Analysis)
- 關鍵財務指標和表現
- 與同業競爭對手比較

## 4. 分析師觀點匯總 (Analyst Consensus)
- 專業機構的評級和目標價
- 近期評級變化和理由

## 5. 風險評估 (Risk Assessment)
- 主要風險因素識別
- 上檔和下檔目標

## 6. 投資建議 (Investment Thesis)
- 短期 (1-3個月) 展望
- 中期 (3-12個月) 趨勢

要求:
- 基於具體事實和數據
- 保持客觀中性的專業角度
- 使用專業財經術語
- 如果資訊不足，請明確指出限制
"""

        try:
            logger.info(f"🤖 使用 Gemini 2.5 Pro 分析 {ticker}...")
            
            response = self.gemini_model.generate_content(
                professional_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # 較低溫度確保專業準確性
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048
                )
            )
            
            return {
                "professional_analysis": response.text,
                "model_used": "gemini-2.0-flash-exp",
                "analysis_type": "professional_financial",
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "content_processed": len(combined_analysis),
                "industry_context": industry
            }
            
        except Exception as e:
            logger.error(f"❌ Gemini 2.5 Pro 分析失敗: {str(e)}")
            return {
                "error": f"Gemini專業分析失敗: {str(e)}",
                "success": False
            }
    
    def _combine_professional_content(self, data_sources: List[Dict[str, Any]]) -> str:
        """整合專業內容，優先處理AI分析數據"""
        
        content_sections = []
        
        for source in data_sources:
            if not source.get('success'):
                continue
            
            # 優先處理 Rhea-AI 專業分析
            rhea_analysis = source.get('rhea_ai_analysis', {})
            if rhea_analysis and any(rhea_analysis.values()):
                ai_sections = []
                
                if rhea_analysis.get('summary'):
                    ai_sections.append(f"AI專業摘要: {rhea_analysis['summary']}")
                
                if rhea_analysis.get('sentiment'):
                    ai_sections.append(f"AI情緒分析: {rhea_analysis['sentiment']}")
                
                if rhea_analysis.get('impact'):
                    ai_sections.append(f"AI影響評估: {rhea_analysis['impact']}")
                
                if rhea_analysis.get('end_of_day'):
                    ai_sections.append(f"收盤數據: {rhea_analysis['end_of_day']}")
                
                if ai_sections:
                    content_sections.append("=== StockTitan AI專業分析 ===\n" + "\n".join(ai_sections))
            
            # 添加相關專業內容
            relevant_content = source.get('relevant_content', '')
            if relevant_content:
                source_name = source.get('source', 'Unknown')
                quality_score = source.get('quality_score', 0)
                content_sections.append(f"=== {source_name} (品質: {quality_score:.1f}) ===\n{relevant_content}")
        
        combined = "\n\n".join(content_sections)
        
        # 智能截斷，保留最重要的內容
        if len(combined) > self.config.max_content_length:
            # 優先保留AI分析和高品質內容
            truncated = combined[:self.config.max_content_length]
            combined = truncated + "\n\n[內容因長度限制被智能截斷，已保留最重要部分]"
        
        return combined
    
    def _format_compatible_result(self, ticker: str, raw_data: List[Dict[str, Any]], 
                                 gemini_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """格式化結果，與原本 script_2.py 完全相容"""
        
        # 創建與原本 script_2.py 相同的 structured_data 格式
        structured_data = {
            "price_data": [],
            "news_events": [],
            "analyst_opinions": [],
            "market_context": [],
            "company_fundamentals": []
        }
        
        # 智能內容分類
        for source in raw_data:
            if not source.get('success'):
                continue
                
            content = source.get('relevant_content', '')
            rhea_data = source.get('rhea_ai_analysis', {})
            
            # 基於關鍵字和AI數據進行分類
            content_item = {
                "content": content[:800],  # 限制長度
                "source": source.get('url', ''),
                "timestamp": source.get('timestamp', ''),
                "quality_score": source.get('quality_score', 0),
                "ai_analysis": rhea_data
            }
            
            # 價格和交易數據
            if any(keyword in content.lower() for keyword in ['price', 'trading', 'volume', 'market']):
                structured_data["price_data"].append(content_item)
            
            # 分析師觀點
            if any(keyword in content.lower() for keyword in ['analyst', 'rating', 'target', 'upgrade', 'downgrade']):
                structured_data["analyst_opinions"].append(content_item)
            
            # 新聞事件
            if any(keyword in content.lower() for keyword in ['announce', 'report', 'release', 'launch']):
                structured_data["news_events"].append(content_item)
            
            # 基本面數據
            if any(keyword in content.lower() for keyword in ['earnings', 'revenue', 'profit', 'guidance']):
                structured_data["company_fundamentals"].append(content_item)
            
            # 市場背景
            else:
                structured_data["market_context"].append(content_item)
        
        # 創建與原本格式相容的返回結果
        return {
            "status": "success",
            "ticker": ticker,
            "raw_information": raw_data,
            "structured_data": structured_data,
            "gemini_professional_analysis": gemini_analysis,  # 新增的專業分析
            "collection_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_sources": len(raw_data),
                "analysis_success": gemini_analysis.get('success', False),
                "total_content_length": sum(len(s.get('relevant_content', '')) for s in raw_data),
                "ai_analysis_found": sum(1 for s in raw_data if s.get('rhea_ai_analysis', {}).get('summary')),
                "method": "StockTitan_Gemini_Pro",
                "cost_estimate": self._calculate_processing_cost(raw_data, gemini_analysis)
            }
        }
    
    def _calculate_content_quality(self, content: str, rhea_ai_data: Dict[str, str]) -> float:
        """計算內容品質分數"""
        
        score = 0.0
        
        # 基礎內容長度分數
        if len(content) > 200:
            score += 0.3
        elif len(content) > 500:
            score += 0.5
        
        # AI分析數據加分
        ai_fields_found = sum(1 for v in rhea_ai_data.values() if v and isinstance(v, str))
        score += ai_fields_found * 0.15
        
        # 專業關鍵字加分
        professional_keywords = ['earnings', 'revenue', 'analyst', 'target', 'guidance']
        keyword_score = sum(0.1 for keyword in professional_keywords if keyword in content.lower())
        score += min(keyword_score, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_processing_cost(self, raw_data: List[Dict[str, Any]], 
                                 gemini_analysis: Dict[str, Any]) -> float:
        """計算處理成本"""
        
        firecrawl_cost = len(raw_data) * 0.5  # $0.5 per page
        gemini_cost = 0.02 if gemini_analysis.get('success') else 0  # ~$0.02 per analysis
        
        return round(firecrawl_cost + gemini_cost, 3)
    
    def _is_data_sufficient(self, data: List[Dict[str, Any]]) -> bool:
        """評估資料充分性"""
        
        if not data:
            return False
        
        # 計算總內容長度
        total_content = sum(len(source.get('relevant_content', '')) for source in data)
        
        # 檢查AI分析數據
        ai_analysis_count = sum(1 for source in data 
                               if source.get('rhea_ai_analysis', {}).get('summary'))
        
        # 計算平均品質分數
        quality_scores = [source.get('quality_score', 0) for source in data if source.get('success')]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        sufficient = (total_content > 800 and avg_quality > 0.5) or ai_analysis_count > 0
        
        logger.info(f"📊 資料充分性評估: 內容={total_content}字, AI分析={ai_analysis_count}個, "
                   f"平均品質={avg_quality:.2f}, 結果={'充分' if sufficient else '不足'}")
        
        return sufficient
    
    def _create_error_response(self, ticker: str, error_message: str) -> Dict[str, Any]:
        """創建錯誤響應"""
        
        return {
            "status": "error",
            "ticker": ticker,
            "error_message": error_message,
            "raw_information": [],
            "structured_data": {
                "price_data": [],
                "news_events": [],
                "analyst_opinions": [],
                "market_context": [],
                "company_fundamentals": []
            },
            "collection_metadata": {
                "timestamp": datetime.now().isoformat(),
                "error": True,
                "method": "StockTitan_Gemini_Pro"
            }
        }
    
    # === 輔助功能函數 ===
    
    def _check_api_limits(self) -> bool:
        """檢查API使用限制"""
        
        now = datetime.now()
        
        # 重置每日計數
        if now.day != self.api_usage_tracker['last_reset_day']:
            self.api_usage_tracker['daily_calls'] = 0
            self.api_usage_tracker['last_reset_day'] = now.day
        
        # 重置每小時計數
        if now.hour != self.api_usage_tracker['last_reset_hour']:
            self.api_usage_tracker['hourly_calls'] = 0
            self.api_usage_tracker['last_reset_hour'] = now.hour
        
        # 檢查限制
        daily_ok = self.api_usage_tracker['daily_calls'] < self.config.daily_api_limit
        hourly_ok = self.api_usage_tracker['hourly_calls'] < self.config.hourly_api_limit
        
        return daily_ok and hourly_ok
    
    def _update_api_usage(self):
        """更新API使用量"""
        self.api_usage_tracker['daily_calls'] += 1
        self.api_usage_tracker['hourly_calls'] += 1
    
    def _check_cache(self, ticker: str) -> Optional[Dict[str, Any]]:
        """檢查快取"""
        if ticker in self.cache:
            cached_time, cached_data = self.cache[ticker]
            hours_elapsed = (time.time() - cached_time) / 3600
            
            if hours_elapsed < self.config.cache_duration_hours:
                return cached_data
        
        return None
    
    def _update_cache(self, ticker: str, data: Dict[str, Any]):
        """更新快取"""
        self.cache[ticker] = (time.time(), data)
    
    def _is_market_hours(self) -> bool:
        """檢查美國市場交易時間"""
        now = datetime.now()
        # 簡化判斷：週一到週五的9-16點 (可以改用pytz做精確時區轉換)
        return 9 <= now.hour <= 16 and now.weekday() < 5
    
    def _is_earnings_season(self) -> bool:
        """檢查是否為財報季"""
        now = datetime.now()
        # 財報季通常是每季度的前6週
        month = now.month
        return month in [1, 2, 4, 5, 7, 8, 10, 11]

# === 與現有系統整合的主要函數 ===

# 全局實例 (單例模式)
_gatherer_instance = None

async def process(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    直接替換原本 script_2.py 中的 process 函數
    完全相容的接口，無需修改其他代碼
    
    Args:
        stock_data: 來自 script_1.py 的股票資料
        
    Returns:
        與原本 script_2.py 相同格式的結果，但使用 StockTitan + Gemini 2.5 Pro
    """
    global _gatherer_instance
    
    # 延遲初始化 (避免導入時的錯誤)
    if _gatherer_instance is None:
        _gatherer_instance = ImprovedInformationGatherer()
    
    return await _gatherer_instance.process(stock_data)

# 測試和驗證函數
async def test_improved_gatherer():
    """測試改良版資訊收集器"""
    
    print("🧪 [YourPods] 測試改良版資訊收集器...")
    
    # 檢查環境配置
    try:
        config = YourPodsConfig()
        print("✅ 環境配置檢查通過")
    except ValueError as e:
        print(f"❌ 配置錯誤: {e}")
        print("請確保 .env 檔案包含必要的API Keys")
        return
    
    # 模擬來自 script_1.py 的輸入
    test_data = {
        "standardized_ticker": "AAPL",
        "company_name": "Apple Inc.",
        "industry": "Technology Hardware",
        "market_status": "open",
        "current_price": 175.0,
        "currency": "USD"
    }
    
    try:
        print(f"📊 測試股票: {test_data['standardized_ticker']}")
        
        # 測試新的process函數
        result = await process(test_data)
        
        print(f"\n✅ 測試完成!")
        print(f"狀態: {result.get('status')}")
        print(f"資料來源: {result.get('collection_metadata', {}).get('data_sources', 0)}個")
        print(f"處理方法: {result.get('collection_metadata', {}).get('method', 'Unknown')}")
        
        if result.get('gemini_professional_analysis', {}).get('success'):
            analysis = result['gemini_professional_analysis']['professional_analysis']
            print(f"🤖 Gemini 2.5 Pro分析成功")
            print(f"分析預覽: {analysis[:150]}...")
        
        # 估算成本
        cost = result.get('collection_metadata', {}).get('cost_estimate', 0)
        print(f"💰 預估成本: ${cost}")
        
        return result
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 運行測試
    asyncio.run(test_improved_gatherer())
