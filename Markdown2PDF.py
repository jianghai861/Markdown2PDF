import os
import sys
import logging
import subprocess
import platform
from pathlib import Path
import json

import markdown
import pdfkit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QProgressBar,
                             QFileDialog, QMessageBox, QLabel, QTextEdit,
                             QGroupBox, QCheckBox, QComboBox, QSpinBox, QTabWidget,
                             QListWidget, QListWidgetItem, QAbstractItemView, QSplitter)
from PyQt5.QtCore import Qt as QtCore_Qt

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('markdown2pdf.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DependencyChecker:
    """依赖检查器"""

    @staticmethod
    def check_python_packages():
        """检查Python包依赖"""
        required_packages = ['markdown2', 'pdfkit', 'PyQt5']
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ 包 {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"✗ 包 {package} 未安装")

        return missing_packages

    @staticmethod
    def install_package(package_name):
        """安装Python包"""
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package_name])
            logger.info(f"✓ 成功安装包 {package_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ 安装包 {package_name} 失败: {e}")
            return False


class WkHtmlToPdfManager:
    """wkhtmltopdf管理器"""

    def __init__(self):
        self.config_file = 'wkhtmltopdf_config.json'
        self.wkhtmltopdf_path = None
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.wkhtmltopdf_path = config.get('wkhtmltopdf_path')
                    logger.info(f"从配置文件加载路径: {self.wkhtmltopdf_path}")
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}")

    def save_config(self, path):
        """保存配置文件"""
        try:
            config = {'wkhtmltopdf_path': path}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def find_wkhtmltopdf(self):
        """查找wkhtmltopdf路径"""
        # 如果已有配置且路径有效，直接返回
        if self.wkhtmltopdf_path and os.path.exists(self.wkhtmltopdf_path):
            return self.wkhtmltopdf_path

        # 搜索可能的路径
        possible_paths = [
            # 程序目录下的bin文件夹
            os.path.join(os.path.dirname(os.path.abspath(
                __file__)), 'bin', 'wkhtmltopdf.exe'),
            # 程序目录
            os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'wkhtmltopdf.exe'),
            # 系统默认安装路径
            'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
            'C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
            # 用户目录
            os.path.expanduser('~\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'),
            # 可能的手动安装路径
            'D:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
            'E:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
        ]

        # 检查环境变量PATH
        if 'PATH' in os.environ:
            for path_dir in os.environ['PATH'].split(os.pathsep):
                wk_path = os.path.join(path_dir, 'wkhtmltopdf.exe')
                if os.path.exists(wk_path):
                    possible_paths.append(wk_path)

        # 尝试每个路径
        for path in possible_paths:
            if os.path.exists(path):
                self.wkhtmltopdf_path = path
                self.save_config(path)
                logger.info(f"找到wkhtmltopdf: {path}")
                return path

        logger.error("未找到wkhtmltopdf")
        return None

    def validate_wkhtmltopdf(self, path=None):
        """验证wkhtmltopdf是否可用"""
        if not path:
            path = self.wkhtmltopdf_path or self.find_wkhtmltopdf()

        if not path or not os.path.exists(path):
            return False, "wkhtmltopdf路径不存在"

        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )

            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"wkhtmltopdf版本: {version_info}")
                return True, version_info
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                return False, f"执行失败: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, f"验证异常: {str(e)}"

    def download_wkhtmltopdf(self):
        """提供下载指导"""
        download_url = "https://wkhtmltopdf.org/downloads.html"
        message = f"""未找到wkhtmltopdf工具！

请按照以下步骤操作：
1. 访问官方下载页面：{download_url}
2. 根据您的系统选择合适的版本下载
3. 安装时建议选择完整版（包含GUI组件）
4. 安装完成后重启本程序
5. 或者手动指定wkhtmltopdf.exe的路径

常见安装路径：
- C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe
- C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe

注意：需要下载包含GUI组件的完整版本。"""

        return message

    def get_installation_status(self):
        """获取安装状态信息"""
        status_info = {
            'configured_path': self.wkhtmltopdf_path,
            'path_exists': os.path.exists(self.wkhtmltopdf_path) if self.wkhtmltopdf_path else False,
            'is_valid': False,
            'version': None,
            'error': None
        }

        if self.wkhtmltopdf_path:
            is_valid, result = self.validate_wkhtmltopdf()
            status_info['is_valid'] = is_valid
            if is_valid:
                status_info['version'] = result
            else:
                status_info['error'] = result

        return status_info


# 配置wkhtmltopdf
wk_manager = WkHtmlToPdfManager()
WKHTMLTOPDF_PATH = wk_manager.find_wkhtmltopdf()

# 配置pdfkit
config = pdfkit.configuration(
    wkhtmltopdf=WKHTMLTOPDF_PATH) if WKHTMLTOPDF_PATH else None


class ConvertThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, input_files, output_dir, header_edit, footer_edit,
                 page_size_combo, margin_spinboxes, encoding_combo, is_batch_mode=True):
        super().__init__()
        self.input_files = input_files  # 可以是单个文件或文件列表
        self.output_dir = output_dir
        self.header_edit = header_edit
        self.footer_edit = footer_edit
        self.page_size_combo = page_size_combo
        self.margin_spinboxes = margin_spinboxes
        self.encoding_combo = encoding_combo
        self.is_batch_mode = is_batch_mode

    def run(self):
        try:
            # 检查wkhtmltopdf是否可用
            is_valid, validation_msg = wk_manager.validate_wkhtmltopdf()
            if not is_valid:
                self.error.emit(
                    f'wkhtmltopdf验证失败：{validation_msg}\n\n{wk_manager.download_wkhtmltopdf()}')
                return

            # 统一处理文件列表
            if isinstance(self.input_files, str):
                # 单个文件模式
                files_to_process = [self.input_files]
                total_files = 1
                self.log_message.emit(f"开始转换单个文件...")
            else:
                # 批量模式
                files_to_process = self.input_files
                total_files = len(files_to_process)
                self.log_message.emit(f"开始转换 {total_files} 个文件...")

            if total_files == 0:
                self.error.emit('没有找到要转换的文件！')
                return

            for i, file_path in enumerate(files_to_process, 1):
                try:
                    # 初始化变量
                    header_path = None
                    footer_path = None
                    file_name = os.path.basename(file_path)

                    # 获取文件名和输出路径
                    output_filename = f'{os.path.splitext(file_name)[0]}.pdf'
                    output_path = os.path.abspath(
                        os.path.join(self.output_dir, output_filename))

                    self.log_message.emit(
                        f"[{i}/{total_files}] 正在处理: {file_name}")

                    # 读取Markdown文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_markdown = f.read()

                    # 转换Markdown为HTML（支持数学公式）
                    html_content = self.convert_markdown_with_math(
                        original_markdown)

                    # 处理页眉页脚
                    header = self.header_edit.text().strip()
                    footer = self.footer_edit.text().strip()

                    # 创建临时文件保存页眉页脚HTML
                    header_path = None
                    footer_path = None

                    if header:
                        header_path = os.path.join(
                            self.output_dir, f'header_temp_{i}.html')
                        header_html = self.create_header_footer_html(
                            header, is_header=True)
                        with open(header_path, 'w', encoding='utf-8') as f:
                            f.write(header_html)

                    if footer:
                        footer_path = os.path.join(
                            self.output_dir, f'footer_temp_{i}.html')
                        footer_html = self.create_header_footer_html(
                            footer, is_header=False)
                        with open(footer_path, 'w', encoding='utf-8') as f:
                            f.write(footer_html)

                    # 创建完整的HTML模板
                    html_template = self.create_html_template(html_content)

                    # 配置PDF选项
                    options = self.create_pdf_options(header_path, footer_path)

                    # 执行转换
                    pdfkit.from_string(
                        html_template,
                        output_path,
                        options=options,
                        configuration=config
                    )

                    self.log_message.emit(f"✓ 成功生成: {output_filename}")

                except Exception as e:
                    error_msg = f"处理文件 {file_name if 'file_name' in locals() else '未知文件'} 时出错: {str(e)}"
                    self.log_message.emit(f"✗ {error_msg}")
                    logger.error(error_msg)
                    continue
                finally:
                    # 清理临时文件
                    self.cleanup_temp_files(header_path, footer_path)

                # 更新进度
                progress = int((i / total_files) * 100)
                self.progress.emit(progress)

            self.log_message.emit("转换完成！")
            self.finished.emit()

        except Exception as e:
            error_msg = f"转换过程发生严重错误: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)

    def create_html_template(self, html_content):
        """创建HTML模板，使用本地兼容的数学公式处理"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @charset "UTF-8";
                
                /* 核心字体配置 - 确保所有元素使用相同字体 */
                body, h1, h2, h3, h4, h5, h6, p, div, span, td, th, li {{
                    font-family: 
                        "Segoe UI Emoji",           /* Windows Emoji字体 */
                        "Apple Color Emoji",        /* macOS Emoji字体 */ 
                        "Noto Color Emoji",         /* Google跨平台Emoji字体 */
                        "Segoe UI Symbol",          /* Windows符号字体 */
                        "Symbola",                  /* 专业符号字体 */
                        "DejaVu Sans",              /* 开源字体，良好Unicode支持 */
                        "FreeSans",                 /* GNU FreeFont系列 */
                        "Microsoft YaHei",          /* 微软雅黑 */
                        "SimHei",                   /* 黑体 */
                        Arial,                      /* 基础西文字体 */
                        sans-serif;                 /* 通用备选 */
                }}
                
                body {{ 
                    margin: 40px;
                    line-height: 1.6;
                    font-size: 16px;
                }}
                
                /* 强制所有标题元素使用Emoji友好的字体 */
                h1, h2, h3, h4, h5, h6 {{
                    font-family: inherit !important;
                    font-weight: bold;
                    color: #333333;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    /* 强制启用字体特性 */
                    font-feature-settings: "liga" 1, "dlig" 1 !important;
                    -webkit-font-smoothing: antialiased !important;
                    -moz-osx-font-smoothing: grayscale !important;
                }}
                
                /* 特别针对包含Emoji的标题 */
                h1[id*="emoji"], h2[id*="emoji"], h3[id*="emoji"],
                h1:contains("📋"), h2:contains("📚"), h3:contains("📘") {{
                    font-family: 
                        "Segoe UI Emoji",
                        "Apple Color Emoji", 
                        "Noto Color Emoji",
                        "Symbola",
                        "DejaVu Sans" !important;
                }}
                
                /* 针对特定Emoji符号的特殊处理 */
                .emoji-special {{
                    font-family: 
                        "Segoe UI Emoji",
                        "Apple Color Emoji", 
                        "Noto Color Emoji",
                        "Symbola",
                        "DejaVu Sans" !important;
                    font-feature-settings: "liga" 1, "dlig" 1;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}
                
                /* 强制特定Unicode范围使用Emoji字体 */
                .unicode-emoji {{
                    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji" !important;
                }}
                
                p {{
                    margin: 0 0 16px 0;
                }}
                
                code {{
                    background-color: #f6f8fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                }}
                
                pre {{
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 6px;
                    overflow-x: auto;
                }}
                
                table {{
                    border-collapse: collapse;
                    margin: 16px 0;
                    width: 100%;
                }}
                
                th, td {{
                    border: 1px solid #dfe2e5;
                    padding: 6px 13px;
                }}
                
                th {{
                    background-color: #f6f8fa;
                    font-weight: 600;
                }}
                
                blockquote {{
                    border-left: 4px solid #dfe2e5;
                    padding: 0 16px;
                    margin: 16px 0;
                    color: #6a737d;
                }}
                
                ul, ol {{
                    padding-left: 24px;
                }}
                
                li {{
                    margin: 4px 0;
                }}
                
                /* 数学公式样式 - 使用Unicode和CSS模拟 */
                .math-inline, .math-display {{
                    font-family: "Cambria Math", "Lucida Bright", serif;
                    font-size: 1.1em;
                }}
                
                .math-display {{
                    display: block;
                    text-align: center;
                    margin: 16px 0;
                    padding: 10px;
                    background-color: #f8f8f8;
                    border-radius: 4px;
                }}
                
                /* 特殊数学符号的CSS处理 */
                .integral {{ font-size: 1.3em; vertical-align: middle; }}
                .sum-symbol {{ font-size: 1.4em; vertical-align: middle; }}
                .sqrt-symbol {{ text-decoration: overline; }}
                
                /* 分数样式优化 */
                .fraction {{
                    display: inline-block;
                    text-align: center;
                    line-height: 1;
                    vertical-align: middle;
                }}
                
                .numerator {{
                    display: block;
                    border-bottom: 1px solid black;
                }}
                
                .subscript {{ 
                    font-size: 0.8em; 
                    vertical-align: sub; 
                }}
                
                .superscript {{ 
                    font-size: 0.8em; 
                    vertical-align: super; 
                }}
                
                /* 连续上下标样式 */
                sub, sup {{
                    line-height: 0;
                }}
                
                /* Emoji特定样式 */
                .emoji-icon {{
                    display: inline-block;
                    font-size: 1.2em;
                    line-height: 1;
                    vertical-align: middle;
                }}
                
                /* 预加载关键字符 */
                .preload-emojis {{
                    display: none;
                }}
            </style>
        </head>
        <body>
            <!-- 预加载关键Emoji字符以确保正确渲染 -->
            <div class="preload-emojis">
                &#x1F4CB;&#x1F4DA;&#x1F4D8;&#x2699;&#x1F393;&#x1F4BB;&#x2705;&#x274C;&#x1F504;&#x1F4CA;&#x1F4C1;&#x1F3AF;&#x1F4DD;&#x2728;&#x1F4DE;&#x1F4E7;&#x1F389;&#x1F60A;
                ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
                0123456789!@#$%^&amp;*()_+-=[]{{}}|;':&quot;,./&lt;&gt;?
            </div>
            {html_content}
        </body>
        </html>
        """

    def create_header_footer_html(self, content, is_header=True):
        """创建页眉页脚HTML"""
        css_class = "header" if is_header else "footer"
        position = "top" if is_header else "bottom"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji",
                                 Arial, "Microsoft YaHei", sans-serif;
                }}
                .{css_class} {{ 
                    text-align: center; 
                    font-size: 12px; 
                    color: #666666;
                    padding: 5px 10px;
                    border-{position}: 1px solid #cccccc;
                    background-color: #f9f9f9;
                    margin: 0;
                    width: 100%;
                    box-sizing: border-box;
                    height: 25px;
                    line-height: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="{css_class}">{content}</div>
        </body>
        </html>
        """

    def create_pdf_options(self, header_path, footer_path):
        """创建PDF选项，严格禁止网络访问"""
        # 获取边距值
        margins = {
            'top': f"{self.margin_spinboxes['top'].value()}mm",
            'right': f"{self.margin_spinboxes['right'].value()}mm",
            'bottom': f"{self.margin_spinboxes['bottom'].value()}mm",
            'left': f"{self.margin_spinboxes['left'].value()}mm"
        }
        
        options = {
            'page-size': self.page_size_combo.currentText(),
            'margin-top': margins['top'],
            'margin-right': margins['right'],
            'margin-bottom': margins['bottom'],
            'margin-left': margins['left'],
            'encoding': self.encoding_combo.currentText(),
            'enable-local-file-access': True,
            'disable-external-links': True,      # 禁用外部链接
            'disable-internal-links': True,      # 禁用内部链接
            'no-images': False,                  # 保留图片支持
            'disable-javascript': True,          # 禁用JavaScript（关键！）
            'header-spacing': '5',
            'footer-spacing': '5',
            'footer-right': '[page]/[toPage]',
            'footer-font-size': '10'
        }
        
        # 只有当页眉页脚存在时才添加对应选项
        if header_path:
            options['header-html'] = header_path
        if footer_path:
            options['footer-html'] = footer_path
            
        return options

    def cleanup_temp_files(self, *temp_files):
        """清理临时文件"""
        for temp_file in temp_files:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {temp_file}: {e}")

    def convert_markdown_with_math(self, original_markdown):
        """转换Markdown内容，特别处理数学公式"""
        try:
            # 配置Markdown扩展
            md_extensions = [
                'extra',           # 包含表格、围栏代码块等
                'codehilite',      # 代码高亮
                'toc',             # 目录
                'nl2br',           # 换行处理
                'sane_lists',      # 更好的列表处理
            ]

            # 扩展配置
            extension_configs = {
                'codehilite': {
                    'use_pygments': False,  # 不使用pygments着色器
                    'css_class': 'highlight'
                }
            }

            # 转换基本Markdown
            md = markdown.Markdown(
                extensions=md_extensions,
                extension_configs=extension_configs
            )
            html_content = md.convert(original_markdown)

            # 处理数学公式
            html_content = self.process_math_formulas(
                html_content, original_markdown)

            return html_content

        except Exception as e:
            logger.error(f"Markdown转换失败: {e}")
            # 如果转换失败，回退到简单处理
            return f"<pre>{original_markdown}</pre>"

    def process_math_formulas(self, html_content, original_markdown):
        """处理数学公式，使用本地化方式避免网络依赖"""
        import re

        # 处理行内公式 $...$
        def inline_math_replacer(match):
            formula = match.group(1)
            # 简单的数学符号替换
            formula = self.simplify_math_formula(formula)
            return f'<span class="math-inline">{formula}</span>'

        # 处理块级公式 $$...$$
        def block_math_replacer(match):
            formula = match.group(1)
            # 简单的数学符号替换
            formula = self.simplify_math_formula(formula)
            return f'<div class="math-display">{formula}</div>'

        # 在原始Markdown中查找数学公式并替换
        # 行内公式匹配
        inline_pattern = r'\$(.*?)\$'
        processed_content = re.sub(
            inline_pattern, inline_math_replacer, original_markdown)

        # 块级公式匹配
        block_pattern = r'\$\$(.*?)\$\$'
        processed_content = re.sub(
            block_pattern, block_math_replacer, processed_content, flags=re.DOTALL)

        # 重新转换处理后的Markdown
        try:
            md_extensions = ['extra', 'codehilite', 'nl2br', 'sane_lists']
            md = markdown.Markdown(extensions=md_extensions)
            final_html = md.convert(processed_content)
            return final_html
        except:
            # 如果处理失败，返回原始HTML
            return html_content

    def simplify_math_formula(self, formula):
        """简化数学公式，使用Unicode字符和HTML实体替换"""
        import re

        # 先处理分数格式 /{分子}{分母}
        def fraction_replacer(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f'<span class="fraction"><span class="numerator">{numerator}</span><span>{denominator}</span></span>'

        # 处理 \frac{a}{b} 格式
        def frac_command_replacer(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f'<span class="fraction"><span class="numerator">{numerator}</span><span>{denominator}</span></span>'

        # 处理带上下标的求和符号
        def sum_replacer(match):
            lower = match.group(1)
            upper = match.group(2)
            return f'∑<sub>{lower}</sub><sup>{upper}</sup>'

        # 处理带上下标的积分符号
        def int_replacer(match):
            lower = match.group(1)
            upper = match.group(2)
            return f'∫<sub>{lower}</sub><sup>{upper}</sup>'

        # 处理平方根带次方
        def sqrt_replacer(match):
            index = match.group(1)
            body = match.group(2)
            return f'<sup>{index}</sup>√{body}'

        # 处理特殊的指数格式
        formula = re.sub(r'e\^-([a-zA-Z0-9]+)', r'e<sup>-\1</sup>', formula)
        formula = re.sub(r'e\^\{([^}]+)\}', r'e<sup>\1</sup>', formula)

        # 处理连续的下标和上标
        formula = re.sub(r'_\{([^}]+)\}\^\{([^}]+)\}',
                         r'<sub>\1</sub><sup>\2</sup>', formula)
        formula = re.sub(r'\^\{([^}]+)\}_\{([^}]+)\}',
                         r'<sup>\1</sup><sub>\2</sub>', formula)

        # 处理LaTeX分数 \frac{a}{b}
        formula = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}',
                         frac_command_replacer, formula)

        # 处理简单的分数 a/b
        formula = re.sub(
            r'(\d+)/(\d+)', r'<sup>\1</sup>&frasl;<sub>\2</sub>', formula)

        # 处理带上下标的求和符号 \sum_{i=1}^{n}
        formula = re.sub(
            r'\\sum_\{([^}]+)\}\^\{([^}]+)\}', sum_replacer, formula)

        # 处理带上下标的积分符号 \int_{a}^{b}
        formula = re.sub(
            r'\\int_\{([^}]+)\}\^\{([^}]+)\}', int_replacer, formula)

        # 处理高次方根 \sqrt[n]{x}
        formula = re.sub(r'\\sqrt\[(\d+)\]\{([^}]+)\}', sqrt_replacer, formula)

        # 处理连续的下标和上标（直接使用正则表达式）
        formula = re.sub(r'_\{([^}]+)\}\^\{([^}]+)\}',
                         r'<sub>\1</sub><sup>\2</sup>', formula)
        formula = re.sub(r'\^\{([^}]+)\}_\{([^}]+)\}',
                         r'<sup>\1</sup><sub>\2</sub>', formula)

        # 常见数学符号替换
        replacements = {
            r'\\int': '∫',
            r'\\sum': '∑',
            r'\\prod': '∏',
            r'\\infty': '∞',
            r'\\pm': '±',
            r'\\times': '×',
            r'\\cdot': '·',
            r'\\leq': '≤',
            r'\\geq': '≥',
            r'\\neq': '≠',
            r'\\approx': '≈',
            r'\\sin': 'sin',
            r'\\cos': 'cos',
            r'\\tan': 'tan',
            r'\\log': 'log',
            r'\\ln': 'ln',
            r'\\lim': 'lim',
            # 平均值符号
            r'\\bar\{([^}]+)\}': r'<span style="text-decoration: overline;">\1</span>',
            r'\\partial': '∂',  # 偏导数符号
            r'\\rightarrow': '→',
            # 向量符号
            r'\\vec\{([^}]+)\}': r'<span style="text-decoration: overline;">\1</span>',
            r'\\begin\{pmatrix\}': '(',  # 矩阵开始
            r'\\end\{pmatrix\}': ')',    # 矩阵结束
            r'\\det': 'det',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\delta': 'δ',
            r'\\theta': 'θ',
            r'\\lambda': 'λ',
            r'\\mu': 'μ',
            r'\\pi': 'π',
            r'\\sigma': 'σ',
            r'\\phi': 'φ',
            r'\\omega': 'ω',
            r'\\to': '→',
            r'\\in': '∈',
            r'\\subset': '⊂',
            r'\\cup': '∪',
            r'\\cap': '∩',
            r'\\sqrt': '√',
            r'e\^x': 'eˣ',  # 特殊处理e的x次方
            r'\^2': '²',    # 平方
            r'\^3': '³',    # 立方
            r'_\{([^}]+)\}': r'<sub>\1</sub>',  # 下标 {内容}
            r'_([a-zA-Z0-9])': r'<sub>\1</sub>',   # 单字符下标
            r'\^\{([^}]+)\}': r'<sup>\1</sup>',   # 上标 {内容}
            r'\^([a-zA-Z0-9])': r'<sup>\1</sup>',  # 单字符上标
        }

        result = formula
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result)

        # 处理化学方程式中的特殊格式
        result = re.sub(r'H_2O', 'H₂O', result)
        result = re.sub(r'H_2', 'H₂', result)
        result = re.sub(r'O_2', 'O₂', result)
        result = re.sub(r'CH_4', 'CH₄', result)
        result = re.sub(r'CO_2', 'CO₂', result)

        return result


class SingleFileWidget(QWidget):
    """单个文件转换页面"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)

        # 输入文件
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText('选择要转换的Markdown文件')
        input_button = QPushButton('浏览')
        input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(QLabel('输入文件:'))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_button)
        file_layout.addLayout(input_layout)

        # 输出文件
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText('PDF输出位置（留空则使用源文件同目录）')
        output_button = QPushButton('浏览')
        output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(QLabel('输出文件:'))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_button)
        file_layout.addLayout(output_layout)

        layout.addWidget(file_group)

        # 预览文件名
        self.preview_label = QLabel('输出文件预览: 未选择文件')
        self.preview_label.setStyleSheet('color: #666666; font-style: italic;')
        layout.addWidget(self.preview_label)

        layout.addStretch()

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择Markdown文件',
            '',
            'Markdown Files (*.md);;All Files (*.*)'
        )
        if file_path:
            self.input_edit.setText(file_path)
            self.update_output_preview()
            # 自动设置默认输出路径为源文件同目录
            self.set_default_output_path(file_path)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '选择输出PDF文件',
            '',
            'PDF Files (*.pdf)'
        )
        if file_path:
            self.output_edit.setText(file_path)
            self.update_output_preview()

    def set_default_output_path(self, input_file):
        """设置默认输出路径为源文件同目录"""
        if input_file and os.path.exists(input_file):
            input_dir = os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            default_output = os.path.join(input_dir, f"{base_name}.pdf")
            self.output_edit.setText(default_output)
            self.update_output_preview()

    def update_output_preview(self):
        input_file = self.input_edit.text()
        output_file = self.output_edit.text()

        if input_file and os.path.exists(input_file):
            if not output_file:
                # 如果没有指定输出文件，显示默认路径
                input_dir = os.path.dirname(input_file)
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                preview_text = f'输出文件预览: {os.path.join(input_dir, f"{base_name}.pdf")}'
            else:
                preview_text = f'输出文件预览: {output_file}'
            self.preview_label.setText(preview_text)
            self.preview_label.setStyleSheet(
                'color: #333333; font-style: normal;')
        else:
            self.preview_label.setText('输出文件预览: 未选择文件')
            self.preview_label.setStyleSheet(
                'color: #666666; font-style: italic;')

    def get_input_file(self):
        return self.input_edit.text()

    def get_output_file(self):
        output_file = self.output_edit.text()
        if not output_file and self.input_edit.text():
            # 如果没有指定输出文件，使用默认路径
            input_file = self.input_edit.text()
            input_dir = os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(input_dir, f"{base_name}.pdf")
        return output_file


class BatchConvertWidget(QWidget):
    """批量转换页面"""

    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 文件列表区域
        files_group = QGroupBox("文件列表")
        files_layout = QVBoxLayout(files_group)

        # 文件操作按钮 - 增加文件夹选择按钮
        button_layout = QHBoxLayout()
        add_file_button = QPushButton('添加文件')
        add_file_button.clicked.connect(self.add_files)
        add_folder_button = QPushButton('添加文件夹')
        add_folder_button.clicked.connect(self.add_folder)
        remove_button = QPushButton('移除选中')
        remove_button.clicked.connect(self.remove_selected_files)
        clear_button = QPushButton('清空列表')
        clear_button.clicked.connect(self.clear_files)

        button_layout.addWidget(add_file_button)
        button_layout.addWidget(add_folder_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        files_layout.addLayout(button_layout)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setAlternatingRowColors(True)
        files_layout.addWidget(self.file_list)

        # 文件统计
        self.file_count_label = QLabel('已选择 0 个文件')
        files_layout.addWidget(self.file_count_label)

        layout.addWidget(files_group)

        # 输出文件夹
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout(output_group)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText('选择PDF文件输出文件夹')
        output_button = QPushButton('浏览')
        output_button.clicked.connect(self.select_output_folder)

        output_layout.addWidget(QLabel('输出文件夹:'))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_button)

        layout.addWidget(output_group)

        layout.addStretch()

    def add_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            '选择Markdown文件',
            '',
            'Markdown Files (*.md);;All Files (*.*)'
        )

        if file_paths:
            added_count = 0
            for file_path in file_paths:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setToolTip(file_path)
                    self.file_list.addItem(item)
                    added_count += 1

            if added_count > 0:
                self.update_file_count()
                QMessageBox.information(self, '成功', f'已添加 {added_count} 个新文件')

    def add_folder(self):
        """添加整个文件夹中的所有md文件"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            '选择包含Markdown文件的文件夹'
        )

        if folder_path:
            # 查找文件夹中所有的md文件
            md_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.md'):
                        full_path = os.path.join(root, file)
                        md_files.append(full_path)

            if not md_files:
                QMessageBox.information(self, '提示', '该文件夹中没有找到Markdown文件')
                return

            # 添加找到的文件
            added_count = 0
            skipped_count = 0
            for file_path in md_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    # 显示相对路径或文件名
                    relative_path = os.path.relpath(file_path, folder_path)
                    display_name = relative_path if len(
                        relative_path) < 50 else os.path.basename(file_path)
                    item = QListWidgetItem(display_name)
                    item.setToolTip(file_path)
                    self.file_list.addItem(item)
                    added_count += 1
                else:
                    skipped_count += 1

            self.update_file_count()

            # 显示结果信息
            message = f'从文件夹 "{os.path.basename(folder_path)}" 中找到 {len(md_files)} 个Markdown文件\n'
            message += f'已添加: {added_count} 个文件'
            if skipped_count > 0:
                message += f'\n已存在: {skipped_count} 个文件（已跳过）'

            QMessageBox.information(self, '文件夹添加完成', message)

    def remove_selected_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要移除的文件')
            return

        for item in selected_items:
            row = self.file_list.row(item)
            file_path = self.selected_files[row]
            self.selected_files.remove(file_path)
            self.file_list.takeItem(row)

        self.update_file_count()
        QMessageBox.information(self, '成功', f'已移除 {len(selected_items)} 个文件')

    def clear_files(self):
        if not self.selected_files:
            return

        reply = QMessageBox.question(
            self,
            '确认清除',
            f'确定要清除所有 {len(self.selected_files)} 个已选择的文件吗？',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.selected_files.clear()
            self.file_list.clear()
            self.update_file_count()
            QMessageBox.information(self, '成功', '已清空文件列表')

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输出文件夹')
        if folder:
            self.output_edit.setText(folder)

    def update_file_count(self):
        count = len(self.selected_files)
        self.file_count_label.setText(f'已选择 {count} 个文件')

    def get_selected_files(self):
        return self.selected_files.copy()

    def get_output_folder(self):
        return self.output_edit.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.convert_thread = None
        self.initUI()
        self.check_dependencies()

    def initUI(self):
        self.setWindowTitle('Markdown转PDF工具 v2.5')
        self.setGeometry(150, 150, 750, 650)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 使用分割器优化布局
        main_splitter = QSplitter(QtCore_Qt.Vertical)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_splitter.addWidget(self.tab_widget)

        # 单文件转换页面
        self.single_widget = SingleFileWidget()
        self.tab_widget.addTab(self.single_widget, "单文件转换")

        # 批量转换页面
        self.batch_widget = BatchConvertWidget()
        self.tab_widget.addTab(self.batch_widget, "批量转换")

        # 全局设置区域
        self.setup_global_settings()
        main_splitter.addWidget(self.global_settings_widget)

        # 设置分割器比例
        main_splitter.setSizes([400, 300])

    def setup_global_settings(self):
        """设置全局配置区域 - 恢复原始单列布局"""
        self.global_settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.global_settings_widget)

        # 页面设置区域 - 恢复为单列布局
        page_group = QGroupBox("页面设置")
        page_layout = QVBoxLayout(page_group)

        # 页面尺寸和编码 - 恢复为原来的垂直布局
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(['A4', 'A3', 'Letter', 'Legal'])
        self.page_size_combo.setCurrentText('A4')

        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['UTF-8', 'GBK', 'GB2312'])
        self.encoding_combo.setCurrentText('UTF-8')

        page_layout.addWidget(QLabel('页面尺寸:'))
        page_layout.addWidget(self.page_size_combo)
        page_layout.addWidget(QLabel('编码:'))
        page_layout.addWidget(self.encoding_combo)

        # 边距设置 - 保持原来的布局方式
        margin_group = QGroupBox("页面边距 (毫米)")
        margin_layout = QHBoxLayout(margin_group)

        self.margin_spinboxes = {}
        margins = [('上', 'top'), ('右', 'right'),
                   ('下', 'bottom'), ('左', 'left')]

        for label_text, key in margins:
            layout = QVBoxLayout()
            spinbox = QSpinBox()
            spinbox.setRange(0, 50)
            spinbox.setValue(20 if key in ['top', 'bottom'] else 15)
            self.margin_spinboxes[key] = spinbox
            layout.addWidget(QLabel(label_text))
            layout.addWidget(spinbox)
            margin_layout.addLayout(layout)

        page_layout.addWidget(margin_group)
        settings_layout.addWidget(page_group)

        # 页眉页脚设置
        header_footer_group = QGroupBox("页眉页脚")
        header_footer_layout = QVBoxLayout(header_footer_group)

        self.header_edit = QLineEdit()
        self.header_edit.setPlaceholderText('输入页眉文本（可选）')
        header_footer_layout.addWidget(QLabel('页眉:'))
        header_footer_layout.addWidget(self.header_edit)

        self.footer_edit = QLineEdit()
        self.footer_edit.setPlaceholderText('输入页脚文本（可选）')
        header_footer_layout.addWidget(QLabel('页脚:'))
        header_footer_layout.addWidget(self.footer_edit)

        settings_layout.addWidget(header_footer_group)

        # 日志显示区域
        log_group = QGroupBox("转换日志")
        log_layout = QVBoxLayout(log_group)
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)
        settings_layout.addWidget(log_group)

        # 控制按钮和进度条
        control_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton('开始转换')
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        button_layout.addWidget(self.convert_button)
        button_layout.addStretch()
        control_layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(QtCore_Qt.AlignCenter)
        control_layout.addWidget(self.progress_bar)

        settings_layout.addLayout(control_layout)

    def check_dependencies(self):
        """检查依赖"""
        missing_packages = DependencyChecker.check_python_packages()
        if missing_packages:
            reply = QMessageBox.question(
                self,
                '缺少依赖包',
                f'检测到缺少以下依赖包：\n{", ".join(missing_packages)}\n\n是否自动安装？',
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success_count = 0
                for package in missing_packages:
                    if DependencyChecker.install_package(package):
                        success_count += 1

                if success_count == len(missing_packages):
                    QMessageBox.information(self, '安装完成', '依赖包安装完成，请重启程序。')
                    sys.exit(0)
                else:
                    QMessageBox.warning(self, '安装失败', '部分依赖包安装失败，请手动安装。')

    def start_conversion(self):
        # 根据当前标签页确定转换模式
        current_tab_index = self.tab_widget.currentIndex()

        if current_tab_index == 0:  # 单文件模式
            self.start_single_file_conversion()
        else:  # 批量模式
            self.start_batch_conversion()

    def start_single_file_conversion(self):
        """单文件转换"""
        input_file = self.single_widget.get_input_file()
        output_file = self.single_widget.get_output_file()

        if not input_file:
            QMessageBox.warning(self, '警告', '请选择输入文件！')
            return

        if not os.path.exists(input_file):
            QMessageBox.warning(self, '警告', '输入文件不存在！')
            return

        # 确保输出文件有.pdf扩展名
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, '错误', f'创建输出目录失败：{str(e)}')
                return

        # 检查wkhtmltopdf
        self.check_wkhtmltopdf_and_convert(
            [input_file], output_dir, is_batch_mode=False)

    def start_batch_conversion(self):
        """批量转换"""
        selected_files = self.batch_widget.get_selected_files()
        output_dir = self.batch_widget.get_output_folder()

        if not selected_files:
            QMessageBox.warning(self, '警告', '请至少选择一个文件！')
            return

        if not output_dir:
            QMessageBox.warning(self, '警告', '请选择输出文件夹！')
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                QMessageBox.information(self, '提示', '输出文件夹已创建。')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'创建输出文件夹失败：{str(e)}')
                return

        # 检查wkhtmltopdf
        self.check_wkhtmltopdf_and_convert(
            selected_files, output_dir, is_batch_mode=True)

    def check_wkhtmltopdf_and_convert(self, input_files, output_dir, is_batch_mode):
        """检查wkhtmltopdf并开始转换"""
        is_valid, validation_msg = wk_manager.validate_wkhtmltopdf()
        if not is_valid:
            reply = QMessageBox.question(
                self,
                'wkhtmltopdf未找到',
                f'{validation_msg}\n\n{wk_manager.download_wkhtmltopdf()}\n\n是否手动指定路径？',
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                wk_path, _ = QFileDialog.getOpenFileName(
                    self,
                    '选择wkhtmltopdf.exe',
                    '',
                    'Executable Files (*.exe)'
                )
                if wk_path:
                    wk_manager.wkhtmltopdf_path = wk_path
                    wk_manager.save_config(wk_path)
                    QMessageBox.information(self, '成功', 'wkhtmltopdf路径已设置！')
                else:
                    return
            else:
                return

        # 开始转换
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_display.clear()

        self.convert_thread = ConvertThread(
            input_files,
            output_dir,
            self.header_edit,
            self.footer_edit,
            self.page_size_combo,
            self.margin_spinboxes,
            self.encoding_combo,
            is_batch_mode
        )

        self.convert_thread.progress.connect(self.update_progress)
        self.convert_thread.finished.connect(self.conversion_finished)
        self.convert_thread.error.connect(self.show_error)
        self.convert_thread.log_message.connect(self.add_log_message)
        self.convert_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def add_log_message(self, message):
        self.log_display.append(message)
        # 自动滚动到底部
        scrollbar = self.log_display.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def conversion_finished(self):
        self.convert_button.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, '完成', '转换完成！')

        # 询问是否打开输出位置
        reply = QMessageBox.question(
            self,
            '转换完成',
            '转换已完成！是否打开输出位置？',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                current_tab_index = self.tab_widget.currentIndex()
                if current_tab_index == 0:  # 单文件模式
                    output_file = self.single_widget.get_output_file()
                    output_dir = os.path.dirname(output_file)
                else:  # 批量模式
                    output_dir = self.batch_widget.get_output_folder()

                os.startfile(output_dir)
            except Exception as e:
                QMessageBox.warning(self, '警告', f'无法打开文件夹：{str(e)}')

    def show_error(self, error_msg):
        self.convert_button.setEnabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, '错误', f'转换过程中出现错误：\n{error_msg}')
        self.add_log_message(f"❌ 错误: {error_msg}")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        # 设置应用程序属性
        app.setApplicationName("Markdown转PDF工具")
        app.setApplicationVersion("2.2")

        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        print(f"程序启动失败: {e}")
        sys.exit(1)
