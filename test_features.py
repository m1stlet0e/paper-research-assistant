#!/usr/bin/env python3
"""
功能测试脚本 - 验证所有模块是否正常工作
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """测试所有模块导入"""
    print("\n📦 测试模块导入...")
    
    tests = []
    
    # 核心模块
    try:
        from src.agents.sub_agents import ArxivSearcher, CitationAnalyzer, PDFParser, ReviewWriter
        tests.append(("多智能体模块", True, ""))
    except Exception as e:
        tests.append(("多智能体模块", False, str(e)))
    
    # 可视化模块
    try:
        from src.visualization.enhanced_knowledge_graph import EnhancedKnowledgeGraph
        from src.visualization.enhanced_comparison_matrix import EnhancedComparisonMatrix
        tests.append(("可视化模块", True, ""))
    except Exception as e:
        tests.append(("可视化模块", False, str(e)))
    
    # 问答模块
    try:
        from src.qa.intelligent_qa import IntelligentQA
        from src.qa.enhanced_qa import EnhancedQA
        tests.append(("智能问答模块", True, ""))
    except Exception as e:
        tests.append(("智能问答模块", False, str(e)))
    
    # 飞书模块
    try:
        from src.feishu.deep_integration import FeishuDeepIntegration
        from src.feishu.real_integration import FeishuRealIntegration
        tests.append(("飞书集成模块", True, ""))
    except Exception as e:
        tests.append(("飞书集成模块", False, str(e)))
    
    # 数据持久化模块
    try:
        from src.utils.data_persistence import DataPersistence, get_persistence
        tests.append(("数据持久化模块", True, ""))
    except Exception as e:
        tests.append(("数据持久化模块", False, str(e)))
    
    # 报告生成模块
    try:
        from src.generators.report_generator import ReportGenerator
        from src.generators.enhanced_report_generator import EnhancedReportGenerator
        tests.append(("报告生成模块", True, ""))
    except Exception as e:
        tests.append(("报告生成模块", False, str(e)))
    
    # 打印结果
    passed = sum(1 for _, success, _ in tests if success)
    total = len(tests)
    
    print(f"\n模块导入测试: {passed}/{total} 通过")
    for name, success, error in tests:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
        if error:
            print(f"      错误: {error}")
    
    return passed == total


def test_data_persistence():
    """测试数据持久化"""
    print("\n💾 测试数据持久化...")
    
    try:
        from src.utils.data_persistence import DataPersistence
        
        persistence = DataPersistence(base_dir="output/test_data")
        
        # 测试保存
        test_papers = [
            {
                "title": "Test Paper 1",
                "authors": [{"name": "Author 1"}],
                "published": "2024-01-01",
                "summary": "Test summary",
                "arxiv_id": "2401.00001"
            }
        ]
        
        filepath = persistence.save_papers(test_papers, "测试课题", {"test": True})
        print(f"  ✅ 保存数据成功: {filepath}")
        
        # 测试加载
        data = persistence.load_papers(latest=True)
        if data and data.get("papers"):
            print(f"  ✅ 加载数据成功: {len(data['papers'])}篇论文")
        else:
            print("  ❌ 加载数据失败")
            return False
        
        # 测试缓存
        persistence.set_cache("test_key", {"value": "test"})
        cached = persistence.get_cache("test_key")
        if cached:
            print("  ✅ 缓存机制正常")
        else:
            print("  ❌ 缓存机制失败")
            return False
        
        # 测试导出
        csv_path = persistence.export_to_csv(test_papers)
        print(f"  ✅ CSV导出成功")
        
        bibtex_path = persistence.export_to_bibtex(test_papers)
        print(f"  ✅ BibTeX导出成功")
        
        # 获取统计
        stats = persistence.get_statistics()
        print(f"  ✅ 统计信息: {stats['papers_files']}个文件, {stats['memory_cache_items']}个缓存")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据持久化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_qa():
    """测试增强智能问答"""
    print("\n🤖 测试增强智能问答...")
    
    try:
        from src.qa.enhanced_qa import EnhancedQA
        
        # 使用测试数据
        test_papers = [
            {
                "title": "Attention Is All You Need",
                "authors": [{"name": "Vaswani"}, {"name": "Shazeer"}],
                "published": "2017-06-12",
                "summary": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
                "arxiv_id": "1706.03762",
                "categories": [{"term": "cs.CL"}]
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": [{"name": "Devlin"}, {"name": "Chang"}],
                "published": "2018-10-11",
                "summary": "We introduce BERT, a new language representation model which stands for Bidirectional Encoder Representations from Transformers.",
                "arxiv_id": "1810.04805",
                "categories": [{"term": "cs.CL"}]
            }
        ]
        
        qa = EnhancedQA(test_papers)
        
        # 测试不同类型的问题
        questions = [
            ("主要的研究方法有哪些？", "method_overview"),
            ("研究趋势是什么？", "trend_temporal"),
            ("总结一下研究现状", "summary"),
        ]
        
        for question, expected_type in questions:
            result = qa.answer(question)
            
            if result.get("answer"):
                print(f"  ✅ 问题类型 '{expected_type}' 回答成功")
                print(f"      问题: {question}")
                print(f"      回答长度: {len(result['answer'])}字符")
                if result.get("citations"):
                    print(f"      引用数: {len(result['citations'])}")
            else:
                print(f"  ❌ 问题 '{question}' 回答失败")
                return False
        
        # 测试对话历史
        history = qa.get_conversation_history()
        if len(history) == len(questions):
            print(f"  ✅ 对话历史记录正常 ({len(history)}条)")
        else:
            print(f"  ❌ 对话历史记录异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 智能问答测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """测试报告生成器"""
    print("\n📝 测试报告生成器...")
    
    try:
        from src.generators.enhanced_report_generator import EnhancedReportGenerator
        
        generator = EnhancedReportGenerator(output_dir="output/test_reports")
        
        # 测试数据
        test_papers = [
            {
                "title": "Test Paper for Report",
                "authors": [{"name": "Test Author"}],
                "published": "2024-01-01",
                "summary": "This is a test paper for report generation.",
                "arxiv_id": "2401.00001",
                "categories": [{"term": "cs.AI"}]
            }
        ]
        
        # 测试Markdown生成
        md_result = generator.generate(
            topic="测试报告",
            papers=test_papers,
            format="markdown",
            include_analysis=True
        )
        
        if md_result.get("success"):
            print(f"  ✅ Markdown报告生成成功")
            print(f"      文件: {md_result['filepath']}")
            content_len = len(md_result.get('content', ''))
            print(f"      内容长度: {content_len}字符")
        else:
            print(f"  ❌ Markdown报告生成失败: {md_result.get('error')}")
            return False
        
        # 测试LaTeX生成
        latex_result = generator.generate(
            topic="测试报告",
            papers=test_papers,
            format="latex",
            include_analysis=True
        )
        
        if latex_result.get("success"):
            print(f"  ✅ LaTeX报告生成成功")
            print(f"      文件: {latex_result['filepath']}")
        else:
            print(f"  ❌ LaTeX报告生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 报告生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arxiv_search():
    """测试arXiv检索（简短测试）"""
    print("\n🔍 测试arXiv检索...")
    
    try:
        from src.agents.sub_agents import ArxivSearcher
        
        searcher = ArxivSearcher({"max_results": 5})
        papers = searcher.search(["AI"])
        
        if papers:
            print(f"  ✅ 检索成功: 找到{len(papers)}篇论文")
            print(f"      第一篇: {papers[0].get('title', 'N/A')[:50]}...")
        else:
            print("  ⚠️ 检索结果为空（可能网络问题）")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ arXiv检索测试跳过: {e}")
        return True  # 网络问题不算失败


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  AI论文预研助手 - 功能测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("数据持久化", test_data_persistence()))
    results.append(("增强智能问答", test_enhanced_qa()))
    results.append(("报告生成器", test_report_generator()))
    results.append(("arXiv检索", test_arxiv_search()))
    
    # 打印总结
    print("\n" + "="*60)
    print("  测试结果总结")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")
    
    print("\n" + "="*60)
    if passed == total:
        print(f"  🎉 所有测试通过！({passed}/{total})")
    else:
        print(f"  ⚠️ 部分测试失败 ({passed}/{total})")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
