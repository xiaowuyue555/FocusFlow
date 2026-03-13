import sqlite3
import os

def get_db_path():
    # 读取配置文件以支持动态热切换数据库
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, "data", "active_db.txt")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            custom_path = f.read().strip()
            if custom_path and os.path.exists(os.path.dirname(custom_path)):
                return custom_path
    return os.path.join(base_dir, "data", "tracker.db")

def set_db_path(new_path):
    # 保存新的数据库路径
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_file = os.path.join(base_dir, "data", "active_db.txt")
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_path)

def get_connection():
    return sqlite3.connect(get_db_path())


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # ================= 性能优化：启用 WAL 模式 =================
    # WAL (Write-Ahead Logging) 允许读写并发，提升性能
    # 必须在其他操作之前执行
    cursor.execute('''PRAGMA journal_mode = WAL''')
    
    # 1. 基础活动日志表
    cursor.execute('''CREATE TABLE IF NOT EXISTS activity_log 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, app_name TEXT, file_path TEXT, duration REAL)''')
    
    # 2. 项目树表
    cursor.execute('''CREATE TABLE IF NOT EXISTS projects
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         project_name TEXT, 
         parent_id INTEGER,
         created_at DATETIME,
         FOREIGN KEY (parent_id) REFERENCES projects(id))''')
         
    # 3. 自动化规则表 (某路径自动归属某项目)
    cursor.execute('''CREATE TABLE IF NOT EXISTS project_map 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         project_name TEXT, 
         rule_path TEXT,
         project_id INTEGER,
         FOREIGN KEY (project_id) REFERENCES projects(id))''')
    
    # 4. 文件/程序精确分配表
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_assignment
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         file_path TEXT, 
         project_name TEXT, 
         assigned_at DATETIME,
         project_id INTEGER,
         FOREIGN KEY (project_id) REFERENCES projects(id))''')
    
    # 5. 归档表 (记录项目归档状态)
    cursor.execute('''CREATE TABLE IF NOT EXISTS project_archive
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         project_name TEXT, 
         archived_at DATETIME,
         project_id INTEGER,
         FOREIGN KEY (project_id) REFERENCES projects(id))''')
    
    # 6. 运行时状态 (前端悬浮窗与后台通信用)
    cursor.execute('''CREATE TABLE IF NOT EXISTS runtime_status
        (id INTEGER PRIMARY KEY CHECK (id = 1),
         updated_at DATETIME,
         is_idle INTEGER,
         idle_seconds REAL,
         app_name TEXT,
         file_path TEXT)''')

    # ================= 新增表 =================
    
    # 7. 系统配置表 (如空闲阈值等用户自定义设置)
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_config
        (key TEXT PRIMARY KEY, 
         value TEXT)''')
         
    # 8. 黑/白名单表 (忽略的程序或窗口标题关键字)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ignore_list
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         keyword TEXT UNIQUE,
         created_at DATETIME)''')
    
    # 9. 碎片记录归档表（存储被过滤的碎片记录）
    cursor.execute('''CREATE TABLE IF NOT EXISTS fragment_archive
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         file_path TEXT,
         app_name TEXT,
         duration REAL,
         timestamp DATETIME,
         archived_at DATETIME,
         action TEXT)''')  # action: 'deleted' 或 'merged'

    # 初始化默认配置 (如果不存在的话)
    cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('idle_threshold', '30')")
    
    # ================= 性能优化：创建索引 =================
    
    # 1. timestamp 索引 - 加速时间范围查询（今日统计、过去 7 天趋势）
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp 
                      ON activity_log(timestamp)''')
    
    # 2. file_path 索引 - 加速路径匹配查询（项目自动分配）
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_activity_log_file_path 
                      ON activity_log(file_path)''')
    
    # 3. app_name 索引 - 加速应用筛选查询
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_activity_log_app_name 
                      ON activity_log(app_name)''')
    
    # 4. 复合索引 - 优化同时使用时间和路径的查询
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp_path 
                      ON activity_log(timestamp, file_path)''')
    
    conn.commit()
    conn.close()


def get_config(key, default=None):
    """读取配置项"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default


def set_config(key, value):
    """写入配置项"""
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()


def get_date_range(days_back=0):
    """
    获取日期范围用于区间查询（替代 DATE() 函数，使索引生效）
    
    Args:
        days_back: 往前推多少天（0 表示今天）
    
    Returns:
        tuple: (start_date_str, end_date_str) 格式：'YYYY-MM-DD HH:MM:SS'
    """
    from datetime import datetime, timedelta
    
    if days_back == 0:
        # 今天：从今天 00:00:00 到明天 00:00:00
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        return today.strftime('%Y-%m-%d %H:%M:%S'), tomorrow.strftime('%Y-%m-%d %H:%M:%S')
    else:
        # 过去 N 天：从 N 天前 00:00:00 到今天 23:59:59
        start_date = datetime.now() - timedelta(days=days_back)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')


def init_project_tree():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_projects_parent ON projects(parent_id)
    """)
    
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_parent 
        ON projects(project_name, parent_id)
    """)
    
    conn.commit()
    conn.close()
