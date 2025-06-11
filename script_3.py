# 階段3: 內容分析與結構化階段 (Content Analysis)
content_analysis_instructions = {
    "name": "內容分析與結構化階段 (Content Analysis)",
    "description": "此階段負責將收集到的原始資訊按照三層內容金字塔框架（What/Why/So What）進行深度分析和結構化組織。",
    
    "system_prompt": '''
    你是一位頂級的財經分析師，擅長將複雜的市場資訊轉化為清晰、有洞見的分析框架。你的專長是運用「三層內容金字塔」方法來組織和分析股票相關資訊。
    
    三層內容金字塔框架：
    
    第一層：The "What" (事實層) - 客觀描述發生了什麼
    - 核心驅動事件：今日/近期影響股價的主要催化劑
    - 關鍵市場數據：股價表現、成交量、財報數字等
    - 官方聲明：公司公告、CEO關鍵言論等
    
    第二層：The "Why" (敘事層) - 解釋為什麼會這樣
    - 市場解讀：投資者如何理解這些事實
    - 橫向比較：與同業競爭對手的比較
    - 分析師觀點：專業機構的看法和評估
    
    第三層：The "So What" (洞見層) - 這對投資者意味著什麼
    - 多空論戰：當前市場的看多vs看空觀點
    - 未來展望：對未來趨勢的前瞻性分析
    - 風險提示：潛在的風險因素和關注點
    
    分析要求：
    1. 確保每一層都有具體的事實支撐，避免空泛的描述
    2. 保持客觀中立，呈現多方觀點
    3. 重點突出最關鍵的1-2個驅動因素
    4. 使用具體的數字和引述來支撐論點
    5. 確保分析的邏輯性和連貫性
    
    你的輸出應該是結構化的JSON格式，包含三個層次的詳細分析。
    ''',
    
    "user_prompt_template": '''
    請基於以下收集到的關於股票 {ticker} ({company_name}) 的資訊，運用三層內容金字塔框架進行深度分析：
    
    原始資訊：
    {raw_information}
    
    結構化數據：
    {structured_data}
    
    當前股價：${current_price}
    市場狀態：{market_status}
    行業分類：{industry}
    
    請特別關注：
    1. 識別今日/近期最重要的價格驅動因素
    2. 分析市場對相關事件的反應和解讀
    3. 提供前瞻性的投資洞見和風險評估
    4. 確保所有論點都有具體的資料支撐
    
    請按照三層金字塔框架組織你的分析，確保每一層都內容充實且具有價值。
    ''',
    
    "analysis_framework": {
        "layer_1_what": {
            "core_catalyst": {
                "description": "識別推動股票今日表現的核心事件",
                "requirements": [
                    "必須是具體、可驗證的事件",
                    "需要說明事件的重要性程度",
                    "提供事件發生的準確時間"
                ],
                "examples": [
                    "財報超出預期",
                    "重大併購公告",
                    "監管政策變化",
                    "產品發布",
                    "管理層變動"
                ]
            },
            "key_metrics": {
                "description": "關鍵市場數據和表現指標",
                "required_data": [
                    "股價變動幅度和方向",
                    "成交量與平均成交量對比",
                    "相對大盤表現",
                    "關鍵財務數據（如適用）"
                ],
                "format": "使用具體數字和百分比"
            },
            "official_statements": {
                "description": "官方聲明和關鍵引述",
                "sources": [
                    "公司新聞稿",
                    "SEC申報文件",
                    "財報電話會議",
                    "管理層訪談"
                ],
                "requirements": "必須提供準確的引述和來源"
            }
        },
        
        "layer_2_why": {
            "market_narrative": {
                "description": "市場如何解讀第一層的事實",
                "analysis_points": [
                    "投資者情緒反應",
                    "交易行為模式",
                    "機構投資者立場",
                    "與預期的差異"
                ]
            },
            "peer_comparison": {
                "description": "與同業和競爭對手的比較",
                "comparison_aspects": [
                    "相同事件下的不同反應",
                    "基本面指標對比",
                    "市場地位變化",
                    "競爭優勢分析"
                ]
            },
            "analyst_consensus": {
                "description": "分析師和機構的專業觀點",
                "content_types": [
                    "評級變化和理由",
                    "目標價調整",
                    "投資建議",
                    "風險評估"
                ]
            }
        },
        
        "layer_3_so_what": {
            "bull_bear_thesis": {
                "description": "當前的多空論戰要點",
                "bull_case": [
                    "看多的主要理由",
                    "支撐因素和證據",
                    "上升空間評估"
                ],
                "bear_case": [
                    "看空的主要擔憂",
                    "風險因素識別",
                    "下行風險評估"
                ]
            },
            "forward_outlook": {
                "description": "前瞻性展望和關鍵監控點",
                "time_horizons": [
                    "短期（1-3個月）關注點",
                    "中期（3-12個月）趨勢",
                    "長期投資論述影響"
                ],
                "key_catalysts": "未來可能的重要事件或數據點"
            },
            "risk_assessment": {
                "description": "風險因素和注意事項",
                "risk_categories": [
                    "公司特定風險",
                    "行業系統性風險",
                    "宏觀經濟風險",
                    "監管和政策風險"
                ]
            }
        }
    },
    
    "quality_criteria": {
        "factual_accuracy": "所有事實和數據必須準確可驗證",
        "logical_coherence": "三層之間的邏輯關係清晰",
        "insight_depth": "提供超越表面資訊的深度洞見",
        "actionability": "為投資決策提供有用的參考",
        "balance": "呈現多方觀點，避免偏見"
    },
    
    "output_structure": {
        "layer_1_what": {
            "core_catalyst": "string",
            "key_metrics": {
                "price_change": "string",
                "volume_analysis": "string", 
                "relative_performance": "string",
                "financial_highlights": "string"
            },
            "official_statements": [
                {
                    "source": "string",
                    "quote": "string",
                    "context": "string"
                }
            ]
        },
        "layer_2_why": {
            "market_narrative": "string",
            "peer_comparison": "string",
            "analyst_consensus": "string"
        },
        "layer_3_so_what": {
            "bull_case": "string",
            "bear_case": "string",
            "forward_outlook": "string",
            "risk_factors": "string"
        },
        "analysis_metadata": {
            "confidence_level": "high/medium/low",
            "data_completeness": "percentage",
            "key_assumptions": ["string"],
            "analysis_timestamp": "ISO datetime"
        }
    }
}

# 內容分析階段的實現代碼
content_analysis_code = '''
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('content_analysis')

class ContentAnalyzer:
    """內容分析與結構化階段的處理器"""
    
    def __init__(self, api_key: str = None):
        """初始化內容分析器
        
        Args:
            api_key: 如果需要額外的AI分析服務
        """
        self.api_key = api_key
        self.analysis_templates = self._load_analysis_templates()
        logger.info("ContentAnalyzer initialized")
    
    async def process(self, information_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析並結構化資訊數據
        
        Args:
            information_data: 來自階段2的資訊數據
            
        Returns:
            三層金字塔結構的分析結果
        """
        logger.info(f"Starting content analysis for {information_data.get('ticker')}")
        
        try:
            # 1. 提取關鍵資訊
            key_info = self._extract_key_information(information_data)
            
            # 2. 執行三層分析
            layer_1 = await self._analyze_what_layer(key_info)
            layer_2 = await self._analyze_why_layer(key_info, layer_1)
            layer_3 = await self._analyze_so_what_layer(key_info, layer_1, layer_2)
            
            # 3. 品質檢查
            quality_assessment = self._assess_analysis_quality(layer_1, layer_2, layer_3)
            
            return {
                "status": "success",
                "ticker": information_data.get('ticker'),
                "layer_1_what": layer_1,
                "layer_2_why": layer_2,
                "layer_3_so_what": layer_3,
                "analysis_metadata": {
                    "confidence_level": quality_assessment["confidence"],
                    "data_completeness": quality_assessment["completeness"],
                    "key_assumptions": quality_assessment["assumptions"],
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {
                "status": "error",
                "ticker": information_data.get('ticker'),
                "error_message": str(e),
                "partial_analysis": None
            }
    
    def _extract_key_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """從原始數據中提取關鍵資訊
        
        Args:
            data: 原始資訊數據
            
        Returns:
            提取的關鍵資訊
        """
        structured_data = data.get('structured_data', {})
        
        return {
            "ticker": data.get('ticker'),
            "price_data": structured_data.get('price_data', []),
            "news_events": structured_data.get('news_events', []),
            "analyst_opinions": structured_data.get('analyst_opinions', []),
            "market_context": structured_data.get('market_context', []),
            "company_fundamentals": structured_data.get('company_fundamentals', []),
            "raw_content": self._consolidate_raw_content(data.get('raw_information', []))
        }
    
    def _consolidate_raw_content(self, raw_info: List[Dict[str, Any]]) -> str:
        """整合原始內容文字
        
        Args:
            raw_info: 原始資訊列表
            
        Returns:
            整合後的文字內容
        """
        content_pieces = []
        for item in raw_info:
            if item.get('success') and item.get('response'):
                content = item['response'].get('choices', [{}])[0].get('message', {}).get('content', '')
                if content:
                    content_pieces.append(content)
        
        return '\n\n'.join(content_pieces)
    
    async def _analyze_what_layer(self, key_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析第一層：What - 事實層
        
        Args:
            key_info: 關鍵資訊
            
        Returns:
            第一層分析結果
        """
        # 識別核心催化劑
        core_catalyst = self._identify_core_catalyst(key_info)
        
        # 提取關鍵指標
        key_metrics = self._extract_key_metrics(key_info)
        
        # 提取官方聲明
        official_statements = self._extract_official_statements(key_info)
        
        return {
            "core_catalyst": core_catalyst,
            "key_metrics": key_metrics,
            "official_statements": official_statements
        }
    
    async def _analyze_why_layer(self, key_info: Dict[str, Any], layer_1: Dict[str, Any]) -> Dict[str, Any]:
        """分析第二層：Why - 敘事層
        
        Args:
            key_info: 關鍵資訊
            layer_1: 第一層分析結果
            
        Returns:
            第二層分析結果
        """
        # 分析市場敘事
        market_narrative = self._analyze_market_narrative(key_info, layer_1)
        
        # 同業比較
        peer_comparison = self._analyze_peer_comparison(key_info)
        
        # 分析師共識
        analyst_consensus = self._analyze_analyst_consensus(key_info)
        
        return {
            "market_narrative": market_narrative,
            "peer_comparison": peer_comparison,
            "analyst_consensus": analyst_consensus
        }
    
    async def _analyze_so_what_layer(self, key_info: Dict[str, Any], 
                                   layer_1: Dict[str, Any], 
                                   layer_2: Dict[str, Any]) -> Dict[str, Any]:
        """分析第三層：So What - 洞見層
        
        Args:
            key_info: 關鍵資訊
            layer_1: 第一層分析結果
            layer_2: 第二層分析結果
            
        Returns:
            第三層分析結果
        """
        # 多空論戰
        bull_case = self._identify_bull_case(key_info, layer_1, layer_2)
        bear_case = self._identify_bear_case(key_info, layer_1, layer_2)
        
        # 前瞻展望
        forward_outlook = self._generate_forward_outlook(key_info, layer_1, layer_2)
        
        # 風險評估
        risk_factors = self._assess_risk_factors(key_info, layer_1, layer_2)
        
        return {
            "bull_case": bull_case,
            "bear_case": bear_case,
            "forward_outlook": forward_outlook,
            "risk_factors": risk_factors
        }
    
    def _identify_core_catalyst(self, key_info: Dict[str, Any]) -> str:
        """識別核心催化劑
        
        Args:
            key_info: 關鍵資訊
            
        Returns:
            核心催化劑描述
        """
        # 關鍵詞匹配來識別重要事件
        catalyst_keywords = {
            "earnings": ["earnings", "quarterly", "revenue", "profit", "guidance"],
            "merger": ["merger", "acquisition", "deal", "takeover"],
            "product": ["product", "launch", "release", "innovation"],
            "regulatory": ["FDA", "approval", "regulation", "policy"],
            "management": ["CEO", "executive", "management", "leadership"]
        }
        
        content = key_info.get('raw_content', '').lower()
        
        for catalyst_type, keywords in catalyst_keywords.items():
            if any(keyword in content for keyword in keywords):
                # 這裡應該有更複雜的邏輯來提取具體的事件
                return f"檢測到{catalyst_type}相關的重要事件"
        
        return "未發現明確的特定催化劑"
    
    def _extract_key_metrics(self, key_info: Dict[str, Any]) -> Dict[str, str]:
        """提取關鍵市場指標
        
        Args:
            key_info: 關鍵資訊
            
        Returns:
            關鍵指標字典
        """
        # 這裡應該實現更複雜的數據提取邏輯
        # 暫時返回基本結構
        return {
            "price_change": "需要從price_data中提取",
            "volume_analysis": "需要分析成交量變化", 
            "relative_performance": "需要與大盤比較",
            "financial_highlights": "需要提取財務亮點"
        }
    
    def _extract_official_statements(self, key_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """提取官方聲明
        
        Args:
            key_info: 關鍵資訊
            
        Returns:
            官方聲明列表
        """
        # 這裡應該實現引述提取邏輯
        return [
            {
                "source": "待實現 - 需要解析來源",
                "quote": "待實現 - 需要提取引述",
                "context": "待實現 - 需要提供背景"
            }
        ]
    
    def _analyze_market_narrative(self, key_info: Dict[str, Any], layer_1: Dict[str, Any]) -> str:
        """分析市場敘事"""
        return "待實現 - 市場如何解讀第一層的事實"
    
    def _analyze_peer_comparison(self, key_info: Dict[str, Any]) -> str:
        """分析同業比較"""
        return "待實現 - 與競爭對手和同業的比較分析"
    
    def _analyze_analyst_consensus(self, key_info: Dict[str, Any]) -> str:
        """分析分析師共識"""
        return "待實現 - 分析師觀點和評級匯總"
    
    def _identify_bull_case(self, key_info: Dict[str, Any], layer_1: Dict[str, Any], layer_2: Dict[str, Any]) -> str:
        """識別看多理由"""
        return "待實現 - 看多的主要論點和支撐因素"
    
    def _identify_bear_case(self, key_info: Dict[str, Any], layer_1: Dict[str, Any], layer_2: Dict[str, Any]) -> str:
        """識別看空理由"""
        return "待實現 - 看空的主要擔憂和風險因素"
    
    def _generate_forward_outlook(self, key_info: Dict[str, Any], layer_1: Dict[str, Any], layer_2: Dict[str, Any]) -> str:
        """生成前瞻展望"""
        return "待實現 - 未來趨勢和關鍵關注點"
    
    def _assess_risk_factors(self, key_info: Dict[str, Any], layer_1: Dict[str, Any], layer_2: Dict[str, Any]) -> str:
        """評估風險因素"""
        return "待實現 - 主要風險因素和注意事項"
    
    def _assess_analysis_quality(self, layer_1: Dict[str, Any], layer_2: Dict[str, Any], layer_3: Dict[str, Any]) -> Dict[str, Any]:
        """評估分析品質
        
        Returns:
            品質評估結果
        """
        return {
            "confidence": "medium",  # 需要實際邏輯
            "completeness": 0.8,     # 需要實際計算
            "assumptions": ["需要實現具體的假設識別邏輯"]
        }
    
    def _load_analysis_templates(self) -> Dict[str, Any]:
        """載入分析模板"""
        return {
            "catalyst_patterns": {},
            "metric_extractors": {},
            "narrative_frameworks": {}
        }
'''

print("階段3: 內容分析與結構化階段 (Content Analysis) 指令設計完成")
print(f"三層金字塔框架包含 {len(content_analysis_instructions['analysis_framework'])} 個層次")
print(f"品質評估標準包含 {len(content_analysis_instructions['quality_criteria'])} 個維度")
print(f"輸出結構包含 {len(content_analysis_instructions['output_structure'])} 個主要部分")
print(f"技術實現框架代碼共 {len(content_analysis_code.split('\n'))} 行")