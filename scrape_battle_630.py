#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle 630 数据爬取和得分计算脚本
爬取 https://www.battleverse.cn/battle/630 的数据，统计票数并计算得分
"""

import requests
import json
from datetime import datetime
import time

def fetch_battle_data(fight_id=630):
    """获取对战数据"""
    url = "https://server.battleverse.cn/index/fight/item.do"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {"fightId": fight_id}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None

def process_battle_data(battle_data):
    """处理对战数据，计算票数和得分"""
    if not battle_data or not battle_data.get('success'):
        print("数据获取失败")
        return None
    
    data = battle_data['data']
    creation_list = data.get('creationList', [])
    winner_list = data.get('winnerList', [])  # 获取冠军列表
    
    # 合并所有作品数据（冠军 + 普通作品）
    all_creations = winner_list + creation_list
    
    # 统计每个作品的票数
    results = []
    total_votes = 0
    
    for creation in all_creations:
        creation_id = creation.get('creationId', creation.get('id', 'N/A'))
        user_name = creation.get('userName', '未知用户')
        vote_list = creation.get('voteList', [])
        vote_count = len(vote_list)
        total_votes += vote_count
        
        # 标记是否为冠军
        is_winner = creation.get('winner', 0) == 1
        
        results.append({
            '作品ID': creation_id,
            '用户名': user_name,
            '票数': vote_count,
            '投票者': [voter.get('userName', '未知') for voter in vote_list],
            '创建时间': creation.get('createTime', ''),
            '作品链接': creation.get('creationUrl', ''),
            '是否冠军': '是' if is_winner else '否'
        })
    
    # 先计算得分，然后按得分排序
    
    # 定义特邀评委列表
    special_judges = ["K'K", "AJ", "麦橘MERJIC"]
    
    # 计算得分（最高票数得100分，其他按比例计算），并在满足"冠军 且 票数>15"时额外+30分
    # 同时检查是否有特邀评委，如有则额外+30分
    if results:
        # 先找到最高票数
        max_votes = max(result['票数'] for result in results) if results else 0
        for result in results:
            base_score = 0
            if result['票数'] > 0:
                base_score = (result['票数'] / max_votes) * 100
            
            # 冠军加分
            champion_bonus = 30 if (result.get('是否冠军') == '是' and result.get('票数', 0) > 15) else 0
            
            # 特邀评委加分（分别计算每个评委）
            kk_bonus = 0
            aj_bonus = 0
            merjic_bonus = 0
            voters = result.get('投票者', [])
            for voter in voters:
                if voter == "K'K":
                    kk_bonus = 30
                elif voter == "AJ":
                    aj_bonus = 30
                elif voter == "麦橘MERJIC":
                    merjic_bonus = 30
            
            total_judge_bonus = kk_bonus + aj_bonus + merjic_bonus
            
            result['加分'] = champion_bonus
            result["K'K加分"] = kk_bonus
            result['AJ加分'] = aj_bonus
            result['麦橘MERJIC加分'] = merjic_bonus
            result['特邀评委总分'] = total_judge_bonus
            result['得分'] = round(base_score + champion_bonus + total_judge_bonus, 2)
    else:
        for result in results:
            result['加分'] = 0
            result["K'K加分"] = 0
            result['AJ加分'] = 0
            result['麦橘MERJIC加分'] = 0
            result['特邀评委总分'] = 0
            result['得分'] = 0
    
    # 按最终得分排序
    results.sort(key=lambda x: x['得分'], reverse=True)
    
    return {
        'results': results,
        'total_votes': total_votes,
        'total_creations': len(all_creations),  # 使用合并后的总数
        'winner_count': len(winner_list),  # 添加冠军数量统计
        'battle_info': {
            '名称': data.get('fightNameCn', '未知'),
            '描述': data.get('fightDesc', ''),
            '创建时间': data.get('createTime', ''),
            '结束时间': data.get('endTime', ''),
            '参与用户数': data.get('fightUserCount', 0)
        }
    }

def save_to_excel(data, filename=None):
    """保存数据到Excel文件"""
    # 将 pandas 的导入延迟到实际需要导出时，避免在无服务器环境中引入沉重依赖
    import pandas as pd
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"battle_630_results_{timestamp}.xlsx"
    
    # 准备Excel数据
    excel_data = []
    for result in data['results']:
        excel_data.append({
            '作品ID': result['作品ID'],
            '用户名': result['用户名'],
            '票数': result['票数'],
            '加分': result.get('加分', 0),
            "K'K加分": result.get("K'K加分", 0),
            'AJ加分': result.get('AJ加分', 0),
            '麦橘MERJIC加分': result.get('麦橘MERJIC加分', 0),
            '特邀评委总分': result.get('特邀评委总分', 0),
            '得分': result['得分'],
            '投票者': ', '.join(result['投票者']) if result['投票者'] else '无',
            '创建时间': result['创建时间'],
            '作品链接': result['作品链接']
        })
    
    # 创建DataFrame
    df = pd.DataFrame(excel_data)
    
    # 保存到Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 主数据表
        df.to_excel(writer, sheet_name='投票统计', index=False)
        
        # 汇总信息表
        summary_data = {
            '统计项目': ['总作品数', '总票数', '每票得分', '对战名称', '创建时间', '结束时间', '参与用户数'],
            '数值': [
                data['total_creations'],
                data['total_votes'],
                f"{100.0 / data['total_votes']:.4f}" if data['total_votes'] > 0 else "0",
                data['battle_info']['名称'],
                data['battle_info']['创建时间'],
                data['battle_info']['结束时间'],
                data['battle_info']['参与用户数']
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='汇总信息', index=False)
    
    print(f"数据已保存到: {filename}")
    return filename

def print_summary(data):
    """打印汇总信息"""
    print("\n" + "="*60)
    print("BATTLE 630 投票统计汇总")
    print("="*60)
    print(f"对战名称: {data['battle_info']['名称']}")
    print(f"总作品数: {data['total_creations']}")
    print(f"总票数: {data['total_votes']}")
    print(f"每票得分: {100.0 / data['total_votes']:.4f}" if data['total_votes'] > 0 else "每票得分: 0")
    print(f"创建时间: {data['battle_info']['创建时间']}")
    print(f"结束时间: {data['battle_info']['结束时间']}")
    print(f"参与用户数: {data['battle_info']['参与用户数']}")
    
    print("\n" + "-"*60)
    print("TOP 10 作品排名")
    print("-"*60)
    print(f"{'排名':<4} {'作品ID':<8} {'用户名':<15} {'票数':<6} {'得分':<8}")
    print("-"*60)
    
    for i, result in enumerate(data['results'][:10], 1):
        print(f"{i:<4} {result['作品ID']:<8} {result['用户名']:<15} {result['票数']:<6} {result['得分']:<8}")

def main():
    """主函数"""
    print("开始爬取 Battle 630 数据...")
    
    # 获取数据
    battle_data = fetch_battle_data(630)
    if not battle_data:
        print("数据获取失败，程序退出")
        return
    
    # 处理数据
    processed_data = process_battle_data(battle_data)
    if not processed_data:
        print("数据处理失败，程序退出")
        return
    
    # 打印汇总
    print_summary(processed_data)
    
    # 保存到Excel
    try:
        filename = save_to_excel(processed_data)
        print(f"\nExcel文件已生成: {filename}")
    except Exception as e:
        print(f"保存Excel文件失败: {e}")
    
    # 保存JSON备份
    try:
        json_filename = f"battle_630_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"JSON备份已保存: {json_filename}")
    except Exception as e:
        print(f"保存JSON备份失败: {e}")

if __name__ == "__main__":
    main() 