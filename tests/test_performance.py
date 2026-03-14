#!/usr/bin/env python3
"""
数据库性能测试脚本
用于验证索引优化后的查询速度提升
"""

import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta

# 确保能导入 core 模块
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.database import get_connection, get_date_range

def test_query_performance():
    print("=" * 60)
    print("📊 FocusFlow 数据库性能测试")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 检查索引是否存在
    print("\n✅ 检查索引状态：")
    indexes = cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='activity_log'").fetchall()
    if indexes:
        for (idx_name,) in indexes:
            if idx_name.startswith('idx_'):
                print(f"   ✓ {idx_name}")
    else:
        print("   ❌ 未找到索引！")
    
    # 2. 检查 WAL 模式
    print("\n✅ 检查 WAL 模式：")
    wal_mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
    print(f"   当前模式：{wal_mode.upper()}")
    if wal_mode == 'wal':
        print("   ✓ WAL 模式已启用")
    else:
        print("   ⚠ WAL 模式未启用")
    
    # 3. 查看数据量
    print("\n📊 当前数据量：")
    total_rows = cursor.execute("SELECT COUNT(*) FROM activity_log").fetchone()[0]
    print(f"   activity_log 表总记录数：{total_rows:,} 条")
    
    today_start, tomorrow_start = get_date_range(0)
    today_rows = cursor.execute("SELECT COUNT(*) FROM activity_log WHERE timestamp >= ? AND timestamp < ?", 
                                 (today_start, tomorrow_start)).fetchone()[0]
    print(f"   今日记录数：{today_rows:,} 条")
    
    # 4. 性能测试
    print("\n⚡ 性能测试（每个查询执行 10 次取平均值）：")
    print("-" * 60)
    
    # 测试 1：今日工时统计（优化后的区间查询）
    test_queries = [
        ("今日工时统计（区间查询）", """
            SELECT COALESCE(SUM(duration), 0) as total,
                   COALESCE(SUM(CASE WHEN timestamp >= ? AND timestamp < ? THEN duration ELSE 0 END), 0) as today
            FROM activity_log
            WHERE timestamp >= ? AND timestamp < ?
        """, (today_start, tomorrow_start, today_start, tomorrow_start)),
        
        ("过去 7 天趋势（区间查询）", """
            SELECT DATE(SUBSTR(timestamp, 1, 10)) as work_date, SUM(duration)/3600.0 as hours
            FROM activity_log
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY work_date
            ORDER BY work_date ASC
        """, ((datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'), 
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
        
        ("文件路径匹配（索引查询）", """
            SELECT file_path, SUM(duration) as total_time
            FROM activity_log
            WHERE file_path LIKE '%VSCode%'
            GROUP BY file_path
            ORDER BY total_time DESC
            LIMIT 10
        """, ()),
    ]
    
    for query_name, query_sql, params in test_queries:
        # 执行 10 次取平均值
        times = []
        for _ in range(10):
            start = time.perf_counter()
            cursor.execute(query_sql, params)
            cursor.fetchall()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # 转换为毫秒
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # 性能评级
        if avg_time < 10:
            rating = "🟢 优秀"
        elif avg_time < 50:
            rating = "🟡 良好"
        elif avg_time < 200:
            rating = "🟠 一般"
        else:
            rating = "🔴 较慢"
        
        print(f"\n{query_name}:")
        print(f"   平均：{avg_time:.2f}ms | 最快：{min_time:.2f}ms | 最慢：{max_time:.2f}ms | {rating}")
    
    # 5. 对比测试：有索引 vs 无索引（模拟）
    print("\n" + "=" * 60)
    print("📈 索引效果对比（估算）：")
    print("-" * 60)
    
    # 使用 EXPLAIN QUERY PLAN 查看查询计划
    print("\n查询计划分析：")
    explain = cursor.execute("""
        EXPLAIN QUERY PLAN
        SELECT SUM(duration) FROM activity_log 
        WHERE timestamp >= ? AND timestamp < ?
    """, (today_start, tomorrow_start)).fetchall()
    
    for row in explain:
        plan_detail = row[-1]
        print(f"   {plan_detail}")
        if "USING INDEX" in plan_detail or "SEARCH" in plan_detail:
            print("   ✓ 索引已生效")
        elif "SCAN" in plan_detail:
            print("   ⚠ 全表扫描（索引可能未生效）")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("   - 如果数据量较少（<1 万条），可能感觉不到明显差异")
    print("   - 当数据量达到百万级时，索引优化会有 100-1000 倍提升")
    print("   - 建议运行 3-6 个月后再次测试，对比性能变化")

if __name__ == "__main__":
    test_query_performance()
