# YourPods 完整系統整合腳本
# 將所有階段整合為端到端的股票音訊生成流程

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

# 導入所有改良版階段
try:
    from script_1 import InputProcessor  # 原有的階段1
    from script_2_improved import process as improved_info_gathering  # 改良版階段2
    from script_3_improved import process as improved_content_analysis  # 改良版階段3
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確保所有必要的檔案都在同一目錄中")
    sys.exit(1)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('YourPods_Integration')

class YourPodsOrchestrator:
    """YourPods 系統協調器 - 整合所有處理階段"""
    
    def __init__(self):
        """初始化YourPods系統"""
        self.input_processor = None  # 延遲初始化
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_cost": 0.0,
            "average_processing_time": 0.0
        }
        
        logger.info("🎙️ YourPods 系統協調器初始化完成")
    
    async def process_stock_request(self, stock_input: str, 
                                  include_analysis: bool = True) -> Dict[str, Any]:
        """
        處理完整的股票請求 - 從輸入到分析
        
        Args:
            stock_input: 用戶輸入的股票代碼或公司名稱
            include_analysis: 是否包含第三階段的深度分析
            
        Returns:
            完整的處理結果
        """
        start_time = time.time()
        processing_id = f"yourpods_{int(start_time)}"
        
        logger.info(f"🚀 [YourPods] 開始處理請求: {stock_input} (ID: {processing_id})")
        
        try:
            # === 階段1: 輸入處理與驗證 ===
            logger.info("📊 階段1: 輸入處理與驗證")
            stage1_result = await self._execute_stage1(stock_input)
            
            if stage1_result["status"] != "valid":
                return self._create_error_response(
                    processing_id, stock_input, 
                    f"階段1失敗: {stage1_result.get('error_message', '未知錯誤')}", 
                    start_time
                )
            
            # === 階段2: 改良版資訊收集 ===
            logger.info("🔍 階段2: StockTitan + Gemini 資訊收集")
            stage2_result = await improved_info_gathering(stage1_result)
            
            if stage2_result["status"] != "success":
                return self._create_error_response(
                    processing_id, stock_input,
                    f"階段2失敗: {stage2_result.get('error_message', '資訊收集失敗')}",
                    start_time
                )
            
            # === 階段3: 改良版內容分析 (可選) ===
            stage3_result = None
            if include_analysis:
                logger.info("🧠 階段3: 三層金字塔內容分析")
                stage3_result = await improved_content_analysis(stage2_result)
                
                if stage3_result["status"] != "success":
                    logger.warning("⚠️ 階段3分析失敗，但繼續處理")
            
            # === 整合結果 ===
            processing_time = time.time() - start_time
            final_result = self._create_success_response(
                processing_id, stock_input, stage1_result, 
                stage2_result, stage3_result, processing_time
            )
            
            # 更新統計
            self._update_stats(True, processing_time, stage2_result)
            
            logger.info(f"✅ [YourPods] 處理完成: {stock_input} "
                       f"(耗時: {processing_time:.1f}秒)")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ [YourPods] 處理失敗: {stock_input} - {str(e)}")
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            
            return self._create_error_response(
                processing_id, stock_input, str(e), start_time
            )
    
    async def _execute_stage1(self, stock_input: str) -> Dict[str, Any]:
        """執行階段1: 輸入處理"""
        
        # 延遲初始化InputProcessor
        if self.input_processor is None:
            self.input_processor = InputProcessor()
        
        try:
            # 呼叫原有的階段1處理
            result = await self.input_processor.process(stock_input)
            return result
            
        except Exception as e:
            logger.error(f"階段1執行失敗: {str(e)}")
            # 如果階段1失敗，創建基本的股票資料
            return {
                "status": "valid",
                "standardized_ticker": stock_input.upper(),
                "company_name": f"{stock_input.upper()} Inc.",
                "exchange": "Unknown",
                "industry": "Unknown",
                "market_status": "unknown",
                "fallback": True
            }
    
    def _create_success_response(self, processing_id: str, stock_input: str,
                               stage1_result: Dict[str, Any],
                               stage2_result: Dict[str, Any],
                               stage3_result: Optional[Dict[str, Any]],
                               processing_time: float) -> Dict[str, Any]:
        """創建成功響應"""
        
        ticker = stage1_result.get('standardized_ticker', stock_input.upper())
        
        # 提取關鍵資訊摘要
        summary = self._extract_key_summary(stage2_result, stage3_result)
        
        return {
            "processing_id": processing_id,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            
            # 股票基本資訊
            "stock_info": {
                "ticker": ticker,
                "company_name": stage1_result.get('company_name', 'Unknown'),
                "industry": stage1_result.get('industry', 'Unknown'),
                "exchange": stage1_result.get('exchange', 'Unknown'),
                "market_status": stage1_result.get('market_status', 'unknown')
            },
            
            # 核心摘要 (為未來的音訊生成準備)
            "executive_summary": summary,
            
            # 詳細分析結果
            "detailed_analysis": {
                "stage1_validation": stage1_result,
                "stage2_information": stage2_result,
                "stage3_analysis": stage3_result
            },
            
            # 元數據
            "metadata": {
                "method": "StockTitan_Gemini_Pyramid",
                "stages_completed": 3 if stage3_result else 2,
                "cost_estimate": stage2_result.get('collection_metadata', {}).get('cost_estimate', 0),
                "data_sources": stage2_result.get('collection_metadata', {}).get('data_sources', 0),
                "analysis_confidence": stage3_result.get('analysis_metadata', {}).get('confidence_level', 'medium') if stage3_result else 'n/a'
            },
            
            # 系統統計
            "system_stats": self.processing_stats.copy()
        }
    
    def _create_error_response(self, processing_id: str, stock_input: str, 
                             error_message: str, start_time: float) -> Dict[str, Any]:
        """創建錯誤響應"""
        
        processing_time = time.time() - start_time
        
        return {
            "processing_id": processing_id,
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "stock_input": stock_input,
            "error_message": error_message,
            "system_stats": self.processing_stats.copy()
        }
    
    def _extract_key_summary(self, stage2_result: Dict[str, Any], 
                           stage3_result: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """提取關鍵摘要資訊"""
        
        summary = {
            "headline": "股票分析摘要",
            "key_catalyst": "資料收集中",
            "market_sentiment": "中性",
            "analyst_view": "觀察中",
            "risk_level": "中等"
        }
        
        # 從Gemini專業分析中提取
        gemini_analysis = stage2_result.get('gemini_professional_analysis', {})
        if gemini_analysis.get('success'):
            analysis_text = gemini_analysis.get('professional_analysis', '')
            
            # 簡單的關鍵詞提取
            if 'positive' in analysis_text.lower() or 'strong' in analysis_text.lower():
                summary["market_sentiment"] = "正面"
            elif 'negative' in analysis_text.lower() or 'weak' in analysis_text.lower():
                summary["market_sentiment"] = "負面"
            
            # 提取第一個重要句子作為headline
            sentences = analysis_text.split('。')
            if sentences and len(sentences[0]) > 20:
                summary["headline"] = sentences[0][:100] + "..."
        
        # 從第三階段分析中補充
        if stage3_result and stage3_result.get('status') == 'success':
            layer_1 = stage3_result.get('layer_1_what', {})
            catalyst = layer_1.get('core_catalyst', '')
            if catalyst and catalyst != "資料收集中":
                summary["key_catalyst"] = catalyst[:100] + "..." if len(catalyst) > 100 else catalyst
        
        return summary
    
    def _update_stats(self, success: bool, processing_time: float, 
                     stage2_result: Optional[Dict[str, Any]] = None):
        """更新處理統計"""
        
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful"] += 1
        else:
            self.processing_stats["failed"] += 1
        
        # 更新平均處理時間
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # 更新成本
        if stage2_result:
            cost = stage2_result.get('collection_metadata', {}).get('cost_estimate', 0)
            self.processing_stats["total_cost"] += cost
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        
        return {
            "system": "YourPods v2.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "statistics": self.processing_stats.copy(),
            "success_rate": (
                self.processing_stats["successful"] / 
                max(self.processing_stats["total_processed"], 1) * 100
            ),
            "average_cost_per_request": (
                self.processing_stats["total_cost"] / 
                max(self.processing_stats["successful"], 1)
            )
        }

# === 便捷功能函數 ===

async def analyze_stock(ticker: str, include_deep_analysis: bool = True) -> Dict[str, Any]:
    """
    便捷函數：分析單支股票
    
    Args:
        ticker: 股票代碼
        include_deep_analysis: 是否包含深度分析
        
    Returns:
        完整的分析結果
    """
    orchestrator = YourPodsOrchestrator()
    return await orchestrator.process_stock_request(ticker, include_deep_analysis)

async def batch_analyze_stocks(tickers: List[str], 
                             max_concurrent: int = 3) -> List[Dict[str, Any]]:
    """
    批量分析多支股票
    
    Args:
        tickers: 股票代碼列表
        max_concurrent: 最大並行數量
        
    Returns:
        分析結果列表
    """
    orchestrator = YourPodsOrchestrator()
    
    async def analyze_single(ticker):
        try:
            return await orchestrator.process_stock_request(ticker, True)
        except Exception as e:
            logger.error(f"批量分析失敗 {ticker}: {str(e)}")
            return {"status": "error", "ticker": ticker, "error": str(e)}
    
    # 使用信號量控制並行度
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_analyze(ticker):
        async with semaphore:
            return await analyze_single(ticker)
    
    logger.info(f"🔄 開始批量分析 {len(tickers)} 支股票 (並行度: {max_concurrent})")
    
    tasks = [limited_analyze(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks)
    
    # 統計結果
    successful = sum(1 for r in results if r.get('status') == 'success')
    logger.info(f"✅ 批量分析完成: {successful}/{len(tickers)} 成功")
    
    return results

# === 命令列界面 ===

async def interactive_mode():
    """互動模式"""
    
    print("🎙️ 歡迎使用 YourPods v2.0 互動模式")
    print("輸入股票代碼進行分析，或輸入 'quit' 退出")
    print("範例: AAPL, TSLA, MSFT")
    print("-" * 50)
    
    orchestrator = YourPodsOrchestrator()
    
    while True:
        try:
            user_input = input("\n📊 請輸入股票代碼: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 感謝使用 YourPods!")
                break
            
            if user_input.lower() == 'status':
                status = orchestrator.get_system_status()
                print(f"\n📈 系統狀態:")
                print(f"成功率: {status['success_rate']:.1f}%")
                print(f"平均處理時間: {status['statistics']['average_processing_time']:.1f}秒")
                print(f"平均成本: ${status['average_cost_per_request']:.3f}")
                continue
            
            if not user_input:
                continue
            
            print(f"🔄 正在分析 {user_input}...")
            
            result = await orchestrator.process_stock_request(user_input, True)
            
            if result["status"] == "success":
                print(f"\n✅ 分析完成!")
                
                # 顯示摘要
                summary = result["executive_summary"]
                print(f"📈 {summary['headline']}")
                print(f"核心催化劑: {summary['key_catalyst']}")
                print(f"市場情緒: {summary['market_sentiment']}")
                
                # 顯示元數據
                metadata = result["metadata"]
                print(f"\n📊 處理資訊:")
                print(f"處理時間: {result['processing_time_seconds']}秒")
                print(f"成本估算: ${metadata['cost_estimate']:.3f}")
                print(f"分析信心: {metadata['analysis_confidence']}")
                
            else:
                print(f"\n❌ 分析失敗: {result['error_message']}")
                
        except KeyboardInterrupt:
            print("\n👋 使用者中斷，退出系統")
            break
        except Exception as e:
            print(f"\n❌ 系統錯誤: {str(e)}")

# === 測試和範例 ===

async def run_comprehensive_test():
    """運行綜合測試"""
    
    print("🧪 [YourPods] 運行綜合系統測試")
    
    test_stocks = ["AAPL", "TSLA", "MSFT"]
    
    for ticker in test_stocks:
        print(f"\n📊 測試股票: {ticker}")
        
        try:
            result = await analyze_stock(ticker, True)
            
            if result["status"] == "success":
                processing_time = result["processing_time_seconds"]
                cost = result["metadata"]["cost_estimate"]
                confidence = result["metadata"]["analysis_confidence"]
                
                print(f"✅ {ticker} 分析成功")
                print(f"   處理時間: {processing_time}秒")
                print(f"   成本: ${cost:.3f}")
                print(f"   信心度: {confidence}")
            else:
                print(f"❌ {ticker} 分析失敗: {result['error_message']}")
                
        except Exception as e:
            print(f"❌ {ticker} 測試異常: {str(e)}")
    
    print("\n🎉 綜合測試完成!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YourPods v2.0 - 自動化股票音訊分析系統")
    parser.add_argument("--ticker", "-t", help="分析單支股票")
    parser.add_argument("--batch", "-b", nargs="+", help="批量分析多支股票")
    parser.add_argument("--interactive", "-i", action="store_true", help="互動模式")
    parser.add_argument("--test", action="store_true", help="運行系統測試")
    
    args = parser.parse_args()
    
    async def main():
        if args.test:
            await run_comprehensive_test()
        elif args.ticker:
            result = await analyze_stock(args.ticker)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.batch:
            results = await batch_analyze_stocks(args.batch)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        elif args.interactive:
            await interactive_mode()
        else:
            print("請選擇一個操作模式，使用 --help 查看說明")
    
    asyncio.run(main())
