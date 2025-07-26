#!/usr/bin/env python3
"""
测试推理引擎的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference.logic_engine import compare_scenarios, analyze_solutions, get_recommendations

def test_basic_scenario():
    """测试基本场景"""
    print("=== 测试基本场景 ===")
    
    # 模拟数据
    checks = [
        {"checker": "A", "target": 3, "result": "good"},
        {"checker": "B", "target": 7, "result": "bad"},
    ]
    
    deaths = [
        {"player": 5, "type": "kill"},
        {"player": 2, "type": "vote"},
    ]
    
    judgments = [
        {"player": 4, "label": "bad"},
        {"player": 8, "label": "good"},
    ]
    
    print("输入数据:")
    print(f"查验记录: {checks}")
    print(f"死亡事件: {deaths}")
    print(f"主观判断: {judgments}")
    print()
    
    # 执行推理
    results = compare_scenarios(checks, deaths, judgments)
    
    print("推理结果:")
    print(f"A假设可行解数量: {len(results['A'])}")
    print(f"B假设可行解数量: {len(results['B'])}")
    print()
    
    # 分析结果
    if results["A"]:
        analysis_A = analyze_solutions(results["A"])
        print("A假设下的匪徒概率:")
        for player, prob in sorted(analysis_A["mafia_probability"].items()):
            print(f"  {player}号: {prob:.1%}")
        print()
    
    if results["B"]:
        analysis_B = analyze_solutions(results["B"])
        print("B假设下的匪徒概率:")
        for player, prob in sorted(analysis_B["mafia_probability"].items()):
            print(f"  {player}号: {prob:.1%}")
        print()
    
    # 获取建议
    recommendations = get_recommendations(results)
    print("推理建议:")
    for rec in recommendations:
        print(f"  - {rec}")
    print()

def test_no_solution_scenario():
    """测试无解场景"""
    print("=== 测试无解场景 ===")
    
    # 创建一个矛盾的场景
    checks = [
        {"checker": "A", "target": 3, "result": "good"},
        {"checker": "A", "target": 3, "result": "bad"},  # 矛盾：同一个人被查验出不同结果
    ]
    
    deaths = []
    judgments = []
    
    print("输入数据（矛盾场景）:")
    print(f"查验记录: {checks}")
    print()
    
    results = compare_scenarios(checks, deaths, judgments)
    
    print("推理结果:")
    print(f"A假设可行解数量: {len(results['A'])}")
    print(f"B假设可行解数量: {len(results['B'])}")
    print()
    
    recommendations = get_recommendations(results)
    print("推理建议:")
    for rec in recommendations:
        print(f"  - {rec}")
    print()

if __name__ == "__main__":
    test_basic_scenario()
    test_no_solution_scenario()
    print("测试完成！") 