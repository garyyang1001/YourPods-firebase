# 階段3: 改良版內容分析與結構化 - 整合StockTitan + Gemini資料
# 三層內容金字塔框架 (What/Why/So What)

import json
import logging
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# 如果需要額外的Gemini分析
import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('YourPods_ContentAnalysis')

@dataclass
class AnalysisConfig:
    """內容分析配置"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.use_gemini_enhancement = os.getenv('USE_GEMINI_ENHANCEMENT', 'true').lower() == 'true'
        
        # Gemini配置 (如果需要額外分析)
        if self.gemini_api_key and self.use_gemini_enhancement:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.gemini_model = None
        
        logger.info("✅ YourPods內容分析配置載入完成")

class ImprovedContentAnalyzer:
    """改良版內容分析與結構化處理器 - 整合StockTitan + Gemini數據"""
    
    def __init__(self):
        self.config = AnalysisConfig()
        self.analysis_templates = self._load_analysis_templates()
        logger.info("🧠 YourPods改良版內容分析器初始化完成")
    
    async def process(self, information_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主要處理函數 - 與原本script_3.py完全相容
        
        Args:
            information_data: 來自script_2_improved.py的資訊數據
            
        Returns:
            三層金字塔結構的分析結果
        """
        ticker = information_data.get('ticker')
        logger.info(f"🎯 [YourPods] 開始三層金字塔分析: {ticker}")
        
        try:
            # 1. 智能提取關鍵資訊 (處理新的資料格式)
            key_info = self._extract_enhanced_information(information_data)
            
            # 2. 執行三層金字塔分析
            layer_1 = await self._analyze_what_layer(key_info)
            layer_2 = await self._analyze_why_layer(key_info, layer_1)
            layer_3 = await self._analyze_so_what_layer(key_info, layer_1, layer_2)
            
            # 3. 品質檢查和信心評估
            quality_assessment = self._assess_analysis_quality(layer_1, layer_2, layer_3, key_info)
            
            # 4. 整合Gemini專業分析 (如果可用)
            enhanced_analysis = await self._enhance_with_gemini(key_info, layer_1, layer_2, layer_3)
            
            result = {
                "status": "success",
                "ticker": ticker,
                "layer_1_what": layer_1,
                "layer_2_why": layer_2,
                "layer_3_so_what": layer_3,
                "enhanced_analysis": enhanced_analysis,  # 新增的增強分析
                "analysis_metadata": {
                    "confidence_level": quality_assessment["confidence"],
                    "data_completeness": quality_assessment["completeness"],
                    "key_assumptions": quality_assessment["assumptions"],
                    "analysis_timestamp": datetime.now().isoformat(),
                    "source_method": "StockTitan_Gemini_Enhanced",
                    "pyramid_framework": "What_Why_SoWhat"
                }
            }
            
            logger.info(f"✅ {ticker} 三層金字塔分析完成 - 信心度: {quality_assessment['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ {ticker} 內容分析失敗: {str(e)}")
            return {
                "status": "error",
                "ticker": ticker,
                "error_message": str(e),
                "partial_analysis": None,
                "analysis_metadata": {
                    "analysis_timestamp": datetime.now().isoformat(),
                    "error": True
                }
            }
    
    def _extract_enhanced_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """提取並整合來自StockTitan + Gemini的資訊"""
        
        structured_data = data.get('structured_data', {})
        gemini_analysis = data.get('gemini_professional_analysis', {})
        raw_information = data.get('raw_information', [])
        
        # 整合所有資訊來源
        enhanced_info = {
            "ticker": data.get('ticker'),
            "collection_metadata": data.get('collection_metadata', {}),
            
            # 來自StockTitan的結構化數據
            "price_data": structured_data.get('price_data', []),
            "news_events": structured_data.get('news_events', []),
            "analyst_opinions": structured_data.get('analyst_opinions', []),
            "market_context": structured_data.get('market_context', []),
            "company_fundamentals": structured_data.get('company_fundamentals', []),
            
            # 來自Gemini的專業分析
            "gemini_professional_analysis": gemini_analysis.get('professional_analysis', ''),
            "gemini_success": gemini_analysis.get('success', False),
            
            # Rhea-AI專業數據
            "rhea_ai_insights": self._extract_rhea_ai_insights(raw_information),
            
            # 整合的原始內容
            "consolidated_content": self._consolidate_enhanced_content(raw_information),
            
            # 內容品質指標
            "content_quality_scores": self._calculate_content_scores(structured_data, gemini_analysis, raw_information)
        }
        
        logger.info(f"📊 資訊整合完成 - Gemini分析: {'✅' if enhanced_info['gemini_success'] else '❌'}, "
                   f"AI洞見: {len(enhanced_info['rhea_ai_insights'])}個")
        
        return enhanced_info
    
    def _extract_rhea_ai_insights(self, raw_information: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取所有Rhea-AI專業洞見"""
        
        ai_insights = []
        
        for item in raw_information:
            if item.get('success') and item.get('source') == 'StockTitan_Professional':
                rhea_data = item.get('rhea_ai_analysis', {})
                
                if rhea_data and any(rhea_data.values()):
                    ai_insights.append({
                        'summary': rhea_data.get('summary', ''),
                        'sentiment': rhea_data.get('sentiment', ''),
                        'impact': rhea_data.get('impact', ''),
                        'end_of_day': rhea_data.get('end_of_day', ''),
                        'tags': rhea_data.get('tags', []),
                        'source_url': item.get('url', ''),
                        'timestamp': item.get('timestamp', ''),
                        'quality_score': item.get('quality_score', 0)
                    })
        
        return ai_insights
    
    def _consolidate_enhanced_content(self, raw_information: List[Dict[str, Any]]) -> str:
        """整合增強版原始內容"""
        
        content_pieces = []
        
        # 優先級排序：StockTitan > Backup > Others
        sorted_info = sorted(raw_information, 
                           key=lambda x: (
                               x.get('source') == 'StockTitan_Professional',
                               x.get('quality_score', 0)
                           ), 
                           reverse=True)
        
        for item in sorted_info:
            if item.get('success'):
                relevant_content = item.get('relevant_content', '')
                if relevant_content:
                    source = item.get('source', 'Unknown')
                    quality = item.get('quality_score', 0)
                    content_pieces.append(f"=== {source} (品質: {quality:.1f}) ===\n{relevant_content}")
        
        return '\n\n'.join(content_pieces)
    
    def _calculate_content_scores(self, structured_data: Dict[str, Any], 
                                 gemini_analysis: Dict[str, Any], 
                                 raw_information: List[Dict[str, Any]]) -> Dict[str, float]:
        """計算內容品質分數"""
        
        scores = {
            "overall_quality": 0.0,
            "data_richness": 0.0,
            "ai_analysis_quality": 0.0,
            "source_diversity": 0.0
        }
        
        # 資料豐富度
        total_items = sum(len(structured_data.get(key, [])) for key in structured_data)
        scores["data_richness"] = min(total_items / 10.0, 1.0)  # 10個項目為滿分
        
        # AI分析品質
        if gemini_analysis.get('success'):
            analysis_length = len(gemini_analysis.get('professional_analysis', ''))
            scores["ai_analysis_quality"] = min(analysis_length / 2000.0, 1.0)  # 2000字為滿分
        
        # 來源多樣性
        successful_sources = len([item for item in raw_information if item.get('success')])
        scores["source_diversity"] = min(successful_sources / 5.0, 1.0)  # 5個來源為滿分
        
        # 整體品質
        scores["overall_quality"] = (
            scores["data_richness"] * 0.3 +
            scores["ai_analysis_quality"] * 0.4 +
            scores["source_diversity"] * 0.3
        )
        
        return scores
    
    async def _analyze_what_layer(self, key_info: Dict[str, Any]) -> Dict[str, Any]:
        """第一層分析：What - 事實層"""
        
        logger.info("📊 分析第一層: What (事實層)")
        
        # 識別核心催化劑
        core_catalyst = self._identify_enhanced_catalyst(key_info)
        
        # 提取關鍵指標
        key_metrics = self._extract_enhanced_metrics(key_info)
        
        # 提取官方聲明
        official_statements = self._extract_enhanced_statements(key_info)
        
        return {
            "core_catalyst": core_catalyst,
            "key_metrics": key_metrics,
            "official_statements": official_statements,
            "data_sources_used": self._count_data_sources(key_info)
        }
    
    async def _analyze_why_layer(self, key_info: Dict[str, Any], layer_1: Dict[str, Any]) -> Dict[str, Any]:
        """第二層分析：Why - 敘事層"""
        
        logger.info("🔍 分析第二層: Why (敘事層)")
        
        # 分析市場敘事
        market_narrative = self._analyze_enhanced_narrative(key_info, layer_1)
        
        # 同業比較
        peer_comparison = self._analyze_enhanced_comparison(key_info)
        
        # 分析師共識
        analyst_consensus = self._analyze_enhanced_consensus(key_info)
        
        return {
            "market_narrative": market_narrative,
            "peer_comparison": peer_comparison,
            "analyst_consensus": analyst_consensus,
            "narrative_confidence": self._calculate_narrative_confidence(key_info)
        }
    
    async def _analyze_so_what_layer(self, key_info: Dict[str, Any], 
                                   layer_1: Dict[str, Any], 
                                   layer_2: Dict[str, Any]) -> Dict[str, Any]:
        """第三層分析：So What - 洞見層"""
        
        logger.info("💡 分析第三層: So What (洞見層)")
        
        # 多空論戰
        bull_case = self._identify_enhanced_bull_case(key_info, layer_1, layer_2)
        bear_case = self._identify_enhanced_bear_case(key_info, layer_1, layer_2)
        
        # 前瞻展望
        forward_outlook = self._generate_enhanced_outlook(key_info, layer_1, layer_2)
        
        # 風險評估
        risk_factors = self._assess_enhanced_risks(key_info, layer_1, layer_2)
        
        return {
            "bull_case": bull_case,
            "bear_case": bear_case,
            "forward_outlook": forward_outlook,
            "risk_factors": risk_factors,
            "investment_thesis_strength": self._calculate_thesis_strength(key_info, layer_1, layer_2)
        }
    
    def _identify_enhanced_catalyst(self, key_info: Dict[str, Any]) -> str:
        """增強版催化劑識別 - 利用Rhea-AI和Gemini分析"""
        
        # 優先使用Rhea-AI的summary
        ai_insights = key_info.get('rhea_ai_insights', [])
        if ai_insights:
            primary_summary = ai_insights[0].get('summary', '')
            if primary_summary:
                return f"核心催化劑: {primary_summary[:200]}..."
        
        # 其次使用Gemini分析
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            # 提取第一個重要事件
            catalyst_match = re.search(r'核心事件[：:]\s*([^。\n]{20,100})', gemini_analysis)
            if catalyst_match:
                return f"根據AI分析: {catalyst_match.group(1)}"
        
        # 最後使用關鍵字匹配
        consolidated_content = key_info.get('consolidated_content', '').lower()
        
        catalyst_patterns = {
            "財報發布": ["earnings", "quarterly", "revenue", "profit", "guidance", "財報", "季報"],
            "併購消息": ["merger", "acquisition", "deal", "takeover", "併購", "收購"],
            "產品發布": ["product", "launch", "release", "innovation", "產品", "發布"],
            "監管變化": ["fda", "approval", "regulation", "policy", "監管", "批准"],
            "管理層變動": ["ceo", "executive", "management", "leadership", "管理層", "高管"]
        }
        
        for catalyst_type, keywords in catalyst_patterns.items():
            if any(keyword in consolidated_content for keyword in keywords):
                return f"檢測到{catalyst_type}相關的重要事件"
        
        return "未發現明確的特定催化劑，建議關注整體市場表現"
    
    def _extract_enhanced_metrics(self, key_info: Dict[str, Any]) -> Dict[str, str]:
        """增強版關鍵指標提取"""
        
        metrics = {
            "price_change": "數據收集中",
            "volume_analysis": "數據收集中",
            "relative_performance": "數據收集中", 
            "financial_highlights": "數據收集中"
        }
        
        # 從price_data中提取
        price_data = key_info.get('price_data', [])
        if price_data:
            for item in price_data:
                content = item.get('content', '').lower()
                
                # 提取價格變化資訊
                price_match = re.search(r'(\d+\.?\d*%|\+\d+\.?\d*%|-\d+\.?\d*%)', content)
                if price_match:
                    metrics["price_change"] = f"價格變動: {price_match.group(1)}"
                
                # 提取成交量資訊
                volume_keywords = ["volume", "trading", "成交量"]
                if any(keyword in content for keyword in volume_keywords):
                    metrics["volume_analysis"] = "發現異常成交量活動"
        
        # 從Gemini分析中提取
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            # 提取關鍵數據
            data_match = re.search(r'關鍵數據[：:]\s*([^。\n]{20,150})', gemini_analysis)
            if data_match:
                metrics["financial_highlights"] = data_match.group(1)
        
        return metrics
    
    def _extract_enhanced_statements(self, key_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """增強版官方聲明提取"""
        
        statements = []
        
        # 從AI洞見中提取
        ai_insights = key_info.get('rhea_ai_insights', [])
        for insight in ai_insights:
            summary = insight.get('summary', '')
            if summary and len(summary) > 50:
                statements.append({
                    "source": "StockTitan AI分析",
                    "quote": summary[:200] + "..." if len(summary) > 200 else summary,
                    "context": f"AI情緒: {insight.get('sentiment', 'N/A')}, 影響: {insight.get('impact', 'N/A')}"
                })
        
        # 從新聞事件中提取
        news_events = key_info.get('news_events', [])
        for event in news_events:
            content = event.get('content', '')
            if content and 'announce' in content.lower() or '宣布' in content:
                statements.append({
                    "source": "公司公告",
                    "quote": content[:150] + "..." if len(content) > 150 else content,
                    "context": "來自官方新聞發布"
                })
        
        return statements[:3]  # 限制最多3個聲明
    
    def _analyze_enhanced_narrative(self, key_info: Dict[str, Any], layer_1: Dict[str, Any]) -> str:
        """增強版市場敘事分析"""
        
        # 整合AI洞見中的情緒分析
        ai_insights = key_info.get('rhea_ai_insights', [])
        if ai_insights:
            sentiments = [insight.get('sentiment', '') for insight in ai_insights if insight.get('sentiment')]
            if sentiments:
                primary_sentiment = sentiments[0]
                narrative = f"市場情緒: {primary_sentiment}。"
            else:
                narrative = "市場情緒: 中性。"
        else:
            narrative = "市場情緒: 觀察中。"
        
        # 從Gemini分析中提取市場反應
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            reaction_match = re.search(r'市場反應[：:]\s*([^。\n]{30,200})', gemini_analysis)
            if reaction_match:
                narrative += f" {reaction_match.group(1)}"
        
        # 分析交易行為
        price_data = key_info.get('price_data', [])
        if price_data:
            narrative += " 交易活動顯示投資者對相關事件的積極回應。"
        
        return narrative
    
    def _analyze_enhanced_comparison(self, key_info: Dict[str, Any]) -> str:
        """增強版同業比較"""
        
        # 從Gemini分析中提取比較資訊
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            comparison_match = re.search(r'(同業|競爭|比較)[^。]*([^。]{50,200})', gemini_analysis)
            if comparison_match:
                return f"同業比較: {comparison_match.group(2)}"
        
        # 基於行業分析
        market_context = key_info.get('market_context', [])
        if market_context:
            return "相對於同業，該股票表現符合行業趨勢。需要更多數據進行詳細比較。"
        
        return "同業比較資訊有限，建議關注行業整體表現。"
    
    def _analyze_enhanced_consensus(self, key_info: Dict[str, Any]) -> str:
        """增強版分析師共識"""
        
        analyst_opinions = key_info.get('analyst_opinions', [])
        
        if analyst_opinions:
            # 統計分析師觀點
            total_opinions = len(analyst_opinions)
            consensus_items = []
            
            for opinion in analyst_opinions:
                content = opinion.get('content', '').lower()
                
                if 'upgrade' in content or 'buy' in content or '買入' in content:
                    consensus_items.append("正面")
                elif 'downgrade' in content or 'sell' in content or '賣出' in content:
                    consensus_items.append("負面")
                else:
                    consensus_items.append("中性")
            
            if consensus_items:
                positive_count = consensus_items.count("正面")
                consensus = f"分析師觀點: {total_opinions}位分析師中，{positive_count}位持正面看法"
            else:
                consensus = f"收集到{total_opinions}位分析師觀點，整體較為謹慎"
        else:
            consensus = "分析師覆蓋有限，建議關注官方指引"
        
        # 從Gemini分析中補充
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            analyst_match = re.search(r'分析師[^。]*([^。]{30,150})', gemini_analysis)
            if analyst_match:
                consensus += f"。專業分析: {analyst_match.group(1)}"
        
        return consensus
    
    def _identify_enhanced_bull_case(self, key_info: Dict[str, Any], 
                                   layer_1: Dict[str, Any], 
                                   layer_2: Dict[str, Any]) -> str:
        """增強版看多理由分析"""
        
        bull_points = []
        
        # 從AI洞見中提取正面因素
        ai_insights = key_info.get('rhea_ai_insights', [])
        for insight in ai_insights:
            sentiment = insight.get('sentiment', '').lower()
            impact = insight.get('impact', '').lower()
            
            if 'positive' in sentiment or 'bullish' in sentiment or 'strong' in impact:
                summary = insight.get('summary', '')
                if summary:
                    bull_points.append(summary[:100])
        
        # 從Gemini分析中提取
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            bull_match = re.search(r'(看多|正面|優勢|機會)[^。]*([^。]{50,200})', gemini_analysis)
            if bull_match:
                bull_points.append(bull_match.group(2))
        
        # 從基本面數據中提取
        fundamentals = key_info.get('company_fundamentals', [])
        for item in fundamentals:
            content = item.get('content', '').lower()
            if any(keyword in content for keyword in ['growth', 'profit', 'revenue', 'strong']):
                bull_points.append("基本面表現強勁")
                break
        
        if bull_points:
            return "看多理由: " + "; ".join(bull_points[:3])
        else:
            return "看多理由: 需要更多正面催化劑支撐"
    
    def _identify_enhanced_bear_case(self, key_info: Dict[str, Any], 
                                   layer_1: Dict[str, Any], 
                                   layer_2: Dict[str, Any]) -> str:
        """增強版看空理由分析"""
        
        bear_points = []
        
        # 從AI洞見中提取風險因素
        ai_insights = key_info.get('rhea_ai_insights', [])
        for insight in ai_insights:
            sentiment = insight.get('sentiment', '').lower()
            impact = insight.get('impact', '').lower()
            
            if 'negative' in sentiment or 'bearish' in sentiment or 'weak' in impact:
                summary = insight.get('summary', '')
                if summary:
                    bear_points.append(summary[:100])
        
        # 從Gemini分析中提取風險
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            risk_match = re.search(r'(風險|挑戰|擔憂|負面)[^。]*([^。]{50,200})', gemini_analysis)
            if risk_match:
                bear_points.append(risk_match.group(2))
        
        # 通用風險因素
        bear_points.append("市場整體波動風險")
        
        return "看空擔憂: " + "; ".join(bear_points[:3])
    
    def _generate_enhanced_outlook(self, key_info: Dict[str, Any], 
                                 layer_1: Dict[str, Any], 
                                 layer_2: Dict[str, Any]) -> str:
        """增強版前瞻展望"""
        
        outlook_points = []
        
        # 從Gemini分析中提取前瞻觀點
        gemini_analysis = key_info.get('gemini_professional_analysis', '')
        if gemini_analysis:
            outlook_match = re.search(r'(展望|未來|趨勢|預期)[^。]*([^。]{50,200})', gemini_analysis)
            if outlook_match:
                outlook_points.append(outlook_match.group(2))
        
        # 時間框架分析
        outlook_points.extend([
            "短期(1-3個月): 關注財報季表現和市場情緒",
            "中期(3-12個月): 注意行業趨勢和競爭格局變化",
            "長期: 持續監控基本面改善和成長動能"
        ])
        
        return "前瞻展望: " + "; ".join(outlook_points)
    
    def _assess_enhanced_risks(self, key_info: Dict[str, Any], 
                             layer_1: Dict[str, Any], 
                             layer_2: Dict[str, Any]) -> str:
        """增強版風險評估"""
        
        risk_categories = {
            "公司特定風險": [],
            "行業風險": [],
            "市場風險": ["整體市場波動", "利率變化", "流動性風險"]
        }
        
        # 從內容中識別風險
        consolidated_content = key_info.get('consolidated_content', '').lower()
        
        risk_keywords = {
            "公司特定風險": ["lawsuit", "debt", "management", "competition"],
            "行業風險": ["regulation", "technology", "disruption", "cycle"]
        }
        
        for category, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in consolidated_content:
                    risk_categories[category].append(f"{keyword}相關風險")
        
        # 格式化風險評估
        risk_summary = []
        for category, risks in risk_categories.items():
            if risks:
                risk_summary.append(f"{category}: {', '.join(risks[:2])}")
        
        return "; ".join(risk_summary) if risk_summary else "風險評估: 維持標準市場風險監控"
    
    async def _enhance_with_gemini(self, key_info: Dict[str, Any], 
                                 layer_1: Dict[str, Any], 
                                 layer_2: Dict[str, Any], 
                                 layer_3: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Gemini進行額外的綜合分析增強"""
        
        if not self.config.gemini_model:
            return None
        
        try:
            # 構建綜合分析提示
            enhancement_prompt = f"""
基於以下三層金字塔分析結果，請提供綜合投資洞見：

第一層 (What - 事實):
{json.dumps(layer_1, ensure_ascii=False, indent=2)}

第二層 (Why - 敘事):
{json.dumps(layer_2, ensure_ascii=False, indent=2)}

第三層 (So What - 洞見):
{json.dumps(layer_3, ensure_ascii=False, indent=2)}

請提供：
1. 整體投資建議 (買入/持有/賣出)
2. 關鍵關注點和觸發條件
3. 風險收益評估
4. 適合的投資者類型

請保持客觀專業，避免絕對性建議。
"""
            
            response = self.config.gemini_model.generate_content(
                enhancement_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024
                )
            )
            
            return {
                "comprehensive_analysis": response.text,
                "enhancement_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini增強分析失敗: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # === 輔助功能函數 ===
    
    def _count_data_sources(self, key_info: Dict[str, Any]) -> Dict[str, int]:
        """統計數據來源"""
        return {
            "total_sources": len(key_info.get('rhea_ai_insights', [])),
            "price_data_items": len(key_info.get('price_data', [])),
            "news_items": len(key_info.get('news_events', [])),
            "analyst_opinions": len(key_info.get('analyst_opinions', []))
        }
    
    def _calculate_narrative_confidence(self, key_info: Dict[str, Any]) -> float:
        """計算敘事信心度"""
        
        confidence_factors = []
        
        # Gemini分析品質
        if key_info.get('gemini_success'):
            confidence_factors.append(0.4)
        
        # AI洞見數量
        ai_insights_count = len(key_info.get('rhea_ai_insights', []))
        confidence_factors.append(min(ai_insights_count / 3.0, 0.3))
        
        # 數據豐富度
        total_data_points = sum([
            len(key_info.get('price_data', [])),
            len(key_info.get('news_events', [])),
            len(key_info.get('analyst_opinions', []))
        ])
        confidence_factors.append(min(total_data_points / 10.0, 0.3))
        
        return min(sum(confidence_factors), 1.0)
    
    def _calculate_thesis_strength(self, key_info: Dict[str, Any], 
                                 layer_1: Dict[str, Any], 
                                 layer_2: Dict[str, Any]) -> float:
        """計算投資論述強度"""
        
        strength_score = 0.5  # 基礎分數
        
        # 催化劑清晰度
        catalyst = layer_1.get('core_catalyst', '')
        if '檢測到' in catalyst and '重要事件' in catalyst:
            strength_score += 0.2
        
        # 數據支撐度
        content_scores = key_info.get('content_quality_scores', {})
        strength_score += content_scores.get('overall_quality', 0) * 0.3
        
        return min(strength_score, 1.0)
    
    def _assess_analysis_quality(self, layer_1: Dict[str, Any], 
                               layer_2: Dict[str, Any], 
                               layer_3: Dict[str, Any], 
                               key_info: Dict[str, Any]) -> Dict[str, Any]:
        """評估分析品質"""
        
        # 計算完整性
        completeness_score = 0.0
        
        # 檢查各層內容豐富度
        layer_scores = []
        for layer in [layer_1, layer_2, layer_3]:
            layer_content = str(layer)
            if len(layer_content) > 100:  # 基本內容長度
                layer_scores.append(1.0)
            elif len(layer_content) > 50:
                layer_scores.append(0.5)
            else:
                layer_scores.append(0.0)
        
        completeness_score = sum(layer_scores) / len(layer_scores)
        
        # 確定信心度
        if completeness_score >= 0.8:
            confidence = "high"
        elif completeness_score >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "confidence": confidence,
            "completeness": completeness_score,
            "assumptions": [
                "基於StockTitan和Gemini的專業分析",
                "市場條件可能快速變化",
                "建議結合其他資訊來源進行決策"
            ]
        }
    
    def _load_analysis_templates(self) -> Dict[str, Any]:
        """載入分析模板"""
        return {
            "catalyst_patterns": {
                "earnings": ["earnings", "quarterly", "revenue", "profit"],
                "merger": ["merger", "acquisition", "deal"],
                "product": ["product", "launch", "release"],
                "regulatory": ["FDA", "approval", "regulation"]
            },
            "sentiment_indicators": {
                "positive": ["strong", "growth", "beat", "exceed"],
                "negative": ["weak", "decline", "miss", "concern"]
            }
        }

# === 與現有系統整合的主要函數 ===

# 全局實例
_analyzer_instance = None

async def process(information_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    直接替換原本script_3.py中的process函數
    完全相容的接口，能夠處理來自script_2_improved.py的新資料格式
    
    Args:
        information_data: 來自script_2_improved.py的資訊數據
        
    Returns:
        三層金字塔分析結果，增強版格式
    """
    global _analyzer_instance
    
    if _analyzer_instance is None:
        _analyzer_instance = ImprovedContentAnalyzer()
    
    return await _analyzer_instance.process(information_data)

# 測試函數
async def test_improved_analyzer():
    """測試改良版內容分析器"""
    
    print("🧪 [YourPods] 測試改良版內容分析器...")
    
    # 模擬來自script_2_improved.py的數據
    test_data = {
        "ticker": "AAPL",
        "status": "success",
        "structured_data": {
            "price_data": [{"content": "AAPL price increased 2.5% with high volume"}],
            "news_events": [{"content": "Apple announces new iPhone launch"}],
            "analyst_opinions": [{"content": "Analysts upgrade AAPL to buy rating"}],
            "market_context": [],
            "company_fundamentals": [{"content": "Strong quarterly earnings reported"}]
        },
        "gemini_professional_analysis": {
            "professional_analysis": "Apple shows strong fundamentals with upcoming product launches driving growth. Market sentiment remains positive.",
            "success": True
        },
        "raw_information": [
            {
                "source": "StockTitan_Professional",
                "success": True,
                "rhea_ai_analysis": {
                    "summary": "Apple reports strong quarterly results beating expectations",
                    "sentiment": "Positive",
                    "impact": "Strong positive impact expected"
                }
            }
        ]
    }
    
    try:
        result = await process(test_data)
        
        print(f"✅ 分析完成!")
        print(f"狀態: {result.get('status')}")
        print(f"信心度: {result.get('analysis_metadata', {}).get('confidence_level')}")
        print(f"核心催化劑: {result.get('layer_1_what', {}).get('core_catalyst', 'N/A')[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_improved_analyzer())
