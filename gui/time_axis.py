"""
时间轴组件 - 显示单日时间使用情况
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QSizePolicy, QMenu, QMessageBox, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QFont, QBrush, QPen, QAction

from datetime import datetime, timedelta
from core.database import query_timeline_data


# 应用颜色映射
APP_COLORS = {
    'VSCode': '#0E639C',
    'Chrome': '#4A90D9',
    'Safari': '#5AC8FA',
    '微信': '#07C160',
    'QQ': '#FF9A00',
    'Finder': '#76D7C4',
    'Terminal': '#333333',
    'iTerm2': '#000000',
    'Excel': '#217346',
    'Word': '#2B579A',
    'PowerPoint': '#D24726',
    'PDF': '#F40F02',
    '默认': '#EA77FF',
}


def get_app_color(app_name):
    """获取应用对应的颜色"""
    return APP_COLORS.get(app_name, APP_COLORS['默认'])


def format_duration(seconds):
    """格式化时长显示"""
    seconds = int(round(seconds or 0))
    if seconds < 0:
        return "0 秒"
    if seconds < 60:
        return f"{seconds}秒"
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        if secs > 0:
            return f"{minutes}分{secs}秒"
        return f"{minutes}分"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if minutes > 0:
        return f"{hours}时{minutes}分"
    return f"{hours}时"


def aggregate_timeline_blocks(records, threshold_minutes=5):
    """
    聚合连续的时间块
    
    规则：
    - 同一应用
    - 时间间隔 < threshold_minutes
    - 合并显示
    
    Returns:
        list of dict: [
            {
                'start_time': '08:00',
                'end_time': '09:15',
                'duration': 4500,  # 秒
                'app_name': 'VSCode',
                'files': ['file1.py', 'file2.py'],
                'project_name': 'Project A',
                'color': '#0E639C',
                'original_records': [...]  # 原始记录，用于显示详情
            }
        ]
    """
    if not records:
        return []
    
    blocks = []
    current_block = None
    threshold_seconds = threshold_minutes * 60
    
    for record in records:
        record_time = datetime.fromisoformat(record['timestamp'])
        
        if current_block is None:
            # 创建第一个块
            current_block = {
                'start_time': record_time,
                'end_time': record_time + timedelta(seconds=record['duration']),
                'duration': record['duration'],
                'app_name': record['app_name'],
                'files': [record['file_path']],
                'project_name': record['project_name'],
                'color': get_app_color(record['app_name']),
                'original_records': [record]
            }
        else:
            # 检查是否可以合并
            time_gap = (record_time - current_block['end_time']).total_seconds()
            
            if (record['app_name'] == current_block['app_name'] and 
                time_gap <= threshold_seconds):
                # 合并到当前块
                current_block['end_time'] = record_time + timedelta(seconds=record['duration'])
                current_block['duration'] += record['duration']
                if record['file_path'] not in current_block['files']:
                    current_block['files'].append(record['file_path'])
                current_block['original_records'].append(record)
            else:
                # 保存当前块，创建新块
                blocks.append(current_block)
                current_block = {
                    'start_time': record_time,
                    'end_time': record_time + timedelta(seconds=record['duration']),
                    'duration': record['duration'],
                    'app_name': record['app_name'],
                    'files': [record['file_path']],
                    'project_name': record['project_name'],
                    'color': get_app_color(record['app_name']),
                    'original_records': [record]
                }
    
    # 添加最后一个块
    if current_block:
        blocks.append(current_block)
    
    # 格式化时间
    for block in blocks:
        block['start_time_str'] = block['start_time'].strftime('%H:%M')
        block['end_time_str'] = block['end_time'].strftime('%H:%M')
    
    return blocks


class TimeAxisBlock(QFrame):
    """时间轴块组件"""
    
    def __init__(self, block_data, parent=None):
        super().__init__(parent)
        self.block_data = block_data
        self.setup_ui()
    
    def setup_ui(self):
        """设置 UI"""
        self.setFrameStyle(QFrame.NoFrame)
        self.setContentsMargins(0, 2, 0, 2)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)
        
        # 时间标签（左侧）
        time_label = QLabel(f"{self.block_data['start_time_str']}")
        time_label.setStyleSheet("color: #888888; font-size: 12px; font-weight: bold;")
        time_label.setFixedWidth(50)
        layout.addWidget(time_label)
        
        # 进度条容器
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)
        
        # 彩色进度条
        color_bar = QFrame()
        color_bar.setFixedHeight(20)
        color_bar.setStyleSheet(f"""
            background-color: {self.block_data['color']};
            border-radius: 3px;
        """)
        
        # 计算宽度比例（假设最大块为 2 小时）
        max_duration = 7200  # 2 小时
        width_ratio = min(self.block_data['duration'] / max_duration, 1.0)
        color_bar.setFixedWidth(int(150 * width_ratio))
        
        progress_layout.addWidget(color_bar)
        
        # 应用名称和文件
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # 应用名称
        app_label = QLabel(self.block_data['app_name'])
        app_label.setStyleSheet("color: #D4D4D4; font-size: 13px; font-weight: bold;")
        info_layout.addWidget(app_label)
        
        # 文件路径（简化显示）
        if self.block_data['files']:
            file_name = self.block_data['files'][0].split('/')[-1]
            if len(self.block_data['files']) > 1:
                file_name += f" +{len(self.block_data['files'])-1}个文件"
            
            file_label = QLabel(file_name)
            file_label.setStyleSheet("color: #888888; font-size: 11px;")
            info_layout.addWidget(file_label)
        
        progress_layout.addWidget(info_widget)
        progress_layout.addStretch()
        
        # 时长标签（右侧）
        duration_label = QLabel(format_duration(self.block_data['duration']))
        duration_label.setStyleSheet("color: #CCCCCC; font-size: 12px; font-weight: bold;")
        progress_layout.addWidget(duration_label)
        
        layout.addWidget(progress_container)
        
        # 设置悬停效果
        self.setStyleSheet("""
            TimeAxisBlock {
                background-color: transparent;
                border-radius: 5px;
            }
            TimeAxisBlock:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        
        # 添加点击事件
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """点击显示详情"""
        if event.button() == Qt.LeftButton:
            self.show_details()
    
    def show_details(self):
        """显示详情对话框"""
        from PySide6.QtWidgets import QDialog, QTextEdit, QPushButton
        
        dialog = QDialog(self.window())
        dialog.setWindowTitle(f"{self.block_data['app_name']} - 使用详情")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # 标题信息
        header = QLabel(f"""
            <h3>{self.block_data['app_name']}</h3>
            <p style="color: #888888;">
                {self.block_data['start_time_str']} - {self.block_data['end_time_str']} 
                ({format_duration(self.block_data['duration'])})
            </p>
        """)
        layout.addWidget(header)
        
        # 文件列表
        files_text = QLabel("<b>访问的文件：</b>")
        layout.addWidget(files_text)
        
        files_list = QTextEdit()
        files_list.setReadOnly(True)
        files_content = ""
        for record in self.block_data['original_records']:
            file_path = record['file_path']
            duration = format_duration(record['duration'])
            time = datetime.fromisoformat(record['timestamp']).strftime('%H:%M:%S')
            files_content += f"{time} - {duration}\n{file_path}\n\n"
        
        files_list.setText(files_content.strip())
        layout.addWidget(files_list)
        
        # 项目信息
        if self.block_data['project_name']:
            project_label = QLabel(f"<b>所属项目：</b> {self.block_data['project_name']}")
            project_label.setStyleSheet("color: #4A90D9; font-weight: bold;")
            layout.addWidget(project_label)
        
        # 关闭按钮
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(dialog.accept)
        btn_close.setFixedWidth(100)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec()


class DailyTimelineWidget(QWidget):
    """单日时间轴主组件"""
    
    def __init__(self, date=None, parent=None):
        super().__init__(parent)
        self.date = date if date else datetime.now().strftime('%Y-%m-%d')
        self.app_filter = None
        self.project_filter = None
        self.blocks = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1E1E1E;
            }
            QScrollBar:vertical {
                background-color: #2D2D30;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
        """)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(5)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # 统计信息标签
        self.lbl_stats = QLabel("")
        self.lbl_stats.setStyleSheet("color: #888888; font-size: 12px; padding: 10px;")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_stats)
    
    def load_data(self):
        """加载数据"""
        # 清空现有块
        while self.content_layout.count() > 1:  # 保留 stretch
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 查询数据
        records = query_timeline_data(self.date, self.app_filter, self.project_filter)
        
        if not records:
            # 显示空状态
            empty_label = QLabel("📭 当天暂无数据")
            empty_label.setStyleSheet("color: #888888; font-size: 16px; padding: 50px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.content_layout.insertWidget(0, empty_label)
            self.lbl_stats.setText("")
            return
        
        # 聚合数据块
        self.blocks = aggregate_timeline_blocks(records)
        
        # 创建时间轴块
        for block in self.blocks:
            block_widget = TimeAxisBlock(block)
            self.content_layout.insertWidget(self.content_layout.count() - 1, block_widget)
        
        # 更新统计信息
        total_duration = sum(b['duration'] for b in self.blocks)
        total_apps = len(set(b['app_name'] for b in self.blocks))
        total_records = len(records)
        
        self.lbl_stats.setText(
            f"总计：{format_duration(total_duration)} | "
            f"{total_apps} 个应用 | "
            f"{total_records} 条记录"
        )
    
    def set_date(self, date):
        """设置日期"""
        self.date = date
        self.load_data()
    
    def set_filters(self, app_filter=None, project_filter=None):
        """设置筛选条件"""
        self.app_filter = app_filter
        self.project_filter = project_filter
        self.load_data()
    
    def refresh(self):
        """刷新数据"""
        self.load_data()
