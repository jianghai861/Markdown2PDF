#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wkhtmltopdf 工具综合测试套件
全面验证wkhtmltopdf工具的安装、配置和功能完整性
支持多种测试模式和详细的诊断信息
"""

import os
import sys
import subprocess
import platform
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


class WkhtmltopdfComprehensiveTester:
    """wkhtmltopdf综合测试类"""
    
    def __init__(self):
        self.test_results = []
        self.wkhtmltopdf_path = None
        self.start_time = None
        
    def log_result(self, test_name: str, success: bool, message: str = "", severity: str = "info"):
        """记录测试结果"""
        status_symbols = {
            "pass": "✅",
            "fail": "❌", 
            "warn": "⚠️",
            "info": "ℹ️"
        }
        
        status_texts = {
            "pass": "通过",
            "fail": "失败",
            "warn": "警告", 
            "info": "信息"
        }
        
        symbol = status_symbols.get(severity if not success else "pass", "✅")
        text = status_texts.get(severity if not success else "pass", "通过")
        
        result = f"{symbol} {test_name} - {text}"
        if message:
            result += f" ({message})"
            
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now()
        })
        
        print(result)
        
    def find_wkhtmltopdf_comprehensive(self) -> Optional[str]:
        """
        全面查找wkhtmltopdf路径（增强版查找算法）
        """
        print("\n🔍 正在全面查找wkhtmltopdf...")
        
        search_methods = [
            ("程序目录bin文件夹", self._check_program_bin),
            ("程序根目录", self._check_program_root),
            ("环境变量PATH", self._check_environment_path),
            ("常见安装位置", self._check_common_locations),
            ("注册表查找", self._check_registry),
        ]
        
        for method_name, check_method in search_methods:
            print(f"  检查{method_name}...")
            path = check_method()
            if path:
                print(f"  ✅ 在{method_name}中找到: {path}")
                return path
            else:
                print(f"  ❌ {method_name}中未找到")
                
        print("  💥 未在任何位置找到wkhtmltopdf")
        return None
    
    def _check_program_bin(self) -> Optional[str]:
        """检查程序目录下的bin文件夹"""
        program_dir = os.path.dirname(os.path.abspath(__file__))
        bin_path = os.path.join(program_dir, 'bin', 'wkhtmltopdf.exe')
        return bin_path if os.path.exists(bin_path) else None
    
    def _check_program_root(self) -> Optional[str]:
        """检查程序根目录"""
        program_dir = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.join(program_dir, 'wkhtmltopdf.exe')
        return root_path if os.path.exists(root_path) else None
    
    def _check_environment_path(self) -> Optional[str]:
        """检查环境变量PATH"""
        if 'PATH' not in os.environ:
            return None
            
        for path_dir in os.environ['PATH'].split(os.pathsep):
            if path_dir:
                wk_path = os.path.join(path_dir, 'wkhtmltopdf.exe')
                if os.path.exists(wk_path):
                    return wk_path
        return None
    
    def _check_common_locations(self) -> Optional[str]:
        """检查常见的安装位置"""
        common_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'D:\wkhtmltopdf\bin\wkhtmltopdf.exe',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _check_registry(self) -> Optional[str]:
        """检查Windows注册表"""
        try:
            import winreg
            # 检查常见的注册表位置
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\wkhtmltopdf"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\wkhtmltopdf"),
            ]
            
            for hive, key_path in registry_paths:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        exe_path = os.path.join(install_path, "bin", "wkhtmltopdf.exe")
                        if os.path.exists(exe_path):
                            return exe_path
                except (FileNotFoundError, OSError):
                    continue
        except ImportError:
            pass  # winreg模块不可用
        except Exception:
            pass  # 注册表访问异常
            
        return None
    
    # === 基础安装测试 ===
    
    def test_system_information(self) -> bool:
        """测试系统信息收集"""
        print("\n📋 测试1: 系统环境信息")
        
        try:
            system_info = {
                'os': f"{platform.system()} {platform.release()}",
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
                'processor': platform.processor() or "Unknown"
            }
            
            for key, value in system_info.items():
                self.log_result(f"系统{key}", True, value)
            
            # 检查是否为Windows系统
            if platform.system().lower() != 'windows':
                self.log_result("系统兼容性", False, "当前测试针对Windows系统设计", "warn")
                return False
                
            self.log_result("系统兼容性", True, "Windows系统兼容")
            return True
            
        except Exception as e:
            self.log_result("系统信息收集", False, f"收集异常: {str(e)}")
            return False
    
    def test_basic_installation(self) -> bool:
        """测试基本安装情况"""
        print("\n📋 测试2: 基本安装检测")
        
        self.wkhtmltopdf_path = self.find_wkhtmltopdf_comprehensive()
        
        if self.wkhtmltopdf_path is None:
            self.log_result("基本安装检测", False, "未找到wkhtmltopdf可执行文件")
            return False
            
        self.log_result("基本安装检测", True, f"找到路径: {self.wkhtmltopdf_path}")
        return True
    
    def test_file_integrity(self) -> bool:
        """测试文件完整性"""
        print("\n📋 测试3: 文件完整性验证")
        
        if not self.wkhtmltopdf_path:
            self.log_result("文件完整性验证", False, "没有找到wkhtmltopdf路径")
            return False
            
        checks = [
            ("文件存在性", lambda: os.path.exists(self.wkhtmltopdf_path or "")),
            ("文件类型", lambda: os.path.isfile(self.wkhtmltopdf_path or "")),
            ("文件可读性", lambda: os.access(self.wkhtmltopdf_path or "", os.R_OK)),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.log_result(check_name, True)
                else:
                    self.log_result(check_name, False, "检查失败")
                    all_passed = False
            except Exception as e:
                self.log_result(check_name, False, f"检查异常: {str(e)}")
                all_passed = False
        
        # 文件大小检查
        try:
            if self.wkhtmltopdf_path:
                file_size = os.path.getsize(self.wkhtmltopdf_path)
                size_mb = file_size / (1024 * 1024)
                
                if file_size < 1024:
                    self.log_result("文件大小", False, f"文件过小: {file_size} bytes", "warn")
                    all_passed = False
                elif size_mb > 100:
                    self.log_result("文件大小", True, f"文件较大: {size_mb:.1f} MB", "info")
                else:
                    self.log_result("文件大小", True, f"文件大小正常: {size_mb:.1f} MB")
            else:
                self.log_result("文件大小", False, "路径为空")
                all_passed = False
                
        except Exception as e:
            self.log_result("文件大小", False, f"检查异常: {str(e)}")
            all_passed = False
            
        return all_passed
    
    def test_version_information(self) -> bool:
        """测试版本信息获取"""
        print("\n📋 测试4: 版本信息验证")
        
        if not self.wkhtmltopdf_path:
            self.log_result("版本信息验证", False, "没有找到wkhtmltopdf路径")
            return False
            
        try:
            result = subprocess.run(
                [self.wkhtmltopdf_path, '--version'],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                # 解析版本号
                version_parts = version_info.split()
                if len(version_parts) >= 2:
                    version_number = version_parts[1]
                    self.log_result("版本号解析", True, version_number)
                
                self.log_result("版本命令执行", True, version_info)
                return True
            else:
                error_msg = result.stderr.strip() or f"返回码: {result.returncode}"
                self.log_result("版本命令执行", False, error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("版本命令执行", False, "命令执行超时")
            return False
        except FileNotFoundError:
            self.log_result("版本命令执行", False, "找不到可执行文件")
            return False
        except PermissionError:
            self.log_result("版本命令执行", False, "没有执行权限")
            return False
        except Exception as e:
            self.log_result("版本命令执行", False, f"未知错误: {str(e)}")
            return False
    
    def test_help_documentation(self) -> bool:
        """测试帮助文档获取"""
        print("\n📋 测试5: 帮助文档验证")
        
        if not self.wkhtmltopdf_path:
            self.log_result("帮助文档验证", False, "没有找到wkhtmltopdf路径")
            return False
            
        try:
            result = subprocess.run(
                [self.wkhtmltopdf_path, '--help'],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                help_text = result.stdout.strip()
                help_length = len(help_text)
                
                # 验证帮助文本质量
                keywords = ['Usage:', 'Options:', 'wkhtmltopdf', '--help', '--version']
                found_keywords = [kw for kw in keywords if kw in help_text]
                
                if len(found_keywords) >= 3 and help_length > 200:
                    self.log_result("帮助文档质量", True, f"内容丰富，包含关键信息 ({help_length}字符)")
                    return True
                elif help_length > 50:
                    self.log_result("帮助文档质量", True, f"基础帮助信息可用 ({help_length}字符)", "warn")
                    return True
                else:
                    self.log_result("帮助文档质量", False, f"帮助内容过于简短 ({help_length}字符)")
                    return False
            else:
                error_msg = result.stderr.strip() or f"返回码: {result.returncode}"
                self.log_result("帮助命令执行", False, error_msg)
                return False
                
        except Exception as e:
            self.log_result("帮助文档验证", False, f"执行异常: {str(e)}")
            return False
    
    # === 功能测试 ===
    
    def test_simple_html_conversion(self) -> bool:
        """测试简单HTML转PDF功能"""
        print("\n📋 测试6: 简单HTML转换测试")
        
        if not self.wkhtmltopdf_path:
            self.log_result("HTML转换测试", False, "没有找到wkhtmltopdf路径")
            return False
            
        # 创建临时HTML文件
        temp_html = "temp_test_simple.html"
        temp_pdf = "temp_test_simple.pdf"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>简单转换测试</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .content {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>wkhtmltopdf简单转换测试</h1>
                <p><strong>测试时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            <div class="content">
                <p>这是一个基础的HTML到PDF转换测试。</p>
                <p>如果成功生成PDF文件，说明基础转换功能正常。</p>
            </div>
        </body>
        </html>
        """
        
        return self._execute_conversion_test(temp_html, temp_pdf, html_content, "简单HTML转换")
    
    def test_complex_html_conversion(self) -> bool:
        """测试复杂HTML转PDF功能"""
        print("\n📋 测试7: 复杂HTML转换测试")
        
        if not self.wkhtmltopdf_path:
            self.log_result("复杂HTML转换测试", False, "没有找到wkhtmltopdf路径")
            return False
            
        # 创建复杂的临时HTML文件
        temp_html = "temp_test_complex.html"
        temp_pdf = "temp_test_complex.pdf"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>复杂转换测试</title>
            <style>
                @page {{ 
                    margin: 2cm;
                    @bottom-right {{ content: "第 " counter(page) " 页"; }};
                }}
                body {{ 
                    font-family: 'Microsoft YaHei', Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .cover {{ 
                    text-align: center; 
                    padding: 50px 0;
                    border-bottom: 2px solid #333;
                    margin-bottom: 30px;
                }}
                .section {{ 
                    margin: 20px 0; 
                    padding: 15px;
                    border-left: 3px solid #007acc;
                    background: #f9f9f9;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0;
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: left;
                }}
                th {{ background-color: #f2f2f2; }}
                .highlight {{ background: yellow; padding: 2px 4px; }}
            </style>
        </head>
        <body>
            <div class="cover">
                <h1>wkhtmltopdf复杂转换测试报告</h1>
                <h2>功能完整性验证</h2>
                <p>测试时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h3>1. 文本格式测试</h3>
                <p>这是<strong>粗体文本</strong>，这是<em>斜体文本</em>，这是<u>下划线文本</u>。</p>
                <p>特殊字符测试: © ® ™ € ¥ £ § ¶</p>
                <p>中文测试：<span class="highlight">高亮显示文本</span></p>
            </div>
            
            <div class="section">
                <h3>2. 表格测试</h3>
                <table>
                    <tr><th>功能</th><th>状态</th><th>备注</th></tr>
                    <tr><td>文本渲染</td><td>✅ 正常</td><td>支持多种字体</td></tr>
                    <tr><td>表格布局</td><td>✅ 正常</td><td>CSS样式生效</td></tr>
                    <tr><td>分页处理</td><td>✅ 正常</td><td>自动分页</td></tr>
                    <tr><td>中文支持</td><td>✅ 正常</td><td>完美显示</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>3. 列表测试</h3>
                <ul>
                    <li>项目一：基础功能验证</li>
                    <li>项目二：样式渲染测试</li>
                    <li>项目三：分页效果检查</li>
                </ul>
                <ol>
                    <li>第一步：创建HTML内容</li>
                    <li>第二步：执行转换命令</li>
                    <li>第三步：验证输出结果</li>
                </ol>
            </div>
        </body>
        </html>
        """
        
        return self._execute_conversion_test(temp_html, temp_pdf, html_content, "复杂HTML转换")
    
    def _execute_conversion_test(self, html_file: str, pdf_file: str, content: str, test_name: str) -> bool:
        """执行转换测试的通用方法"""
        try:
            # 写入HTML文件
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 执行转换命令
            cmd = [self.wkhtmltopdf_path, html_file, pdf_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            # 检查转换结果
            conversion_success = (
                result.returncode == 0 and 
                os.path.exists(pdf_file) and 
                os.path.getsize(pdf_file) > 0
            )
            
            if conversion_success:
                pdf_size = os.path.getsize(pdf_file)
                pdf_size_kb = pdf_size / 1024
                self.log_result(test_name, True, f"成功生成PDF文件 ({pdf_size_kb:.1f} KB)")
            else:
                error_detail = result.stderr.strip() or f"返回码: {result.returncode}"
                self.log_result(test_name, False, error_detail)
            
            # 清理临时文件
            self._cleanup_temp_files([html_file, pdf_file])
            return conversion_success
            
        except Exception as e:
            self.log_result(test_name, False, f"转换异常: {str(e)}")
            self._cleanup_temp_files([html_file, pdf_file])
            return False
    
    def _cleanup_temp_files(self, files: List[str]):
        """清理临时文件"""
        for temp_file in files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass  # 忽略删除失败
    
    def test_performance_benchmark(self) -> bool:
        """测试性能基准"""
        print("\n📋 测试8: 性能基准测试")
        
        if not self.wkhtmltopdf_path:
            self.log_result("性能基准测试", False, "没有找到wkhtmltopdf路径")
            return False
        
        import time
        
        # 创建中等复杂度的测试内容
        temp_html = "temp_benchmark.html"
        temp_pdf = "temp_benchmark.pdf"
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>性能测试</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .page { page-break-after: always; }
            </style>
        </head>
        <body>
        """
        
        # 生成多页内容
        for i in range(5):
            html_content += f"""
            <div class="page">
                <h1>性能测试页面 {i+1}</h1>
                <p>这是第{i+1}页的内容，用于测试转换性能。</p>
                <ul>
                    <li>列表项目1</li>
                    <li>列表项目2</li>
                    <li>列表项目3</li>
                </ul>
                <table border="1">
                    <tr><th>列1</th><th>列2</th><th>列3</th></tr>
            """
            for j in range(10):
                html_content += f"<tr><td>数据{j+1}-1</td><td>数据{j+1}-2</td><td>数据{j+1}-3</td></tr>"
            html_content += "</table></div>"
        
        html_content += "</body></html>"
        
        try:
            # 写入文件
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 执行性能测试
            start_time = time.time()
            result = subprocess.run(
                [self.wkhtmltopdf_path, temp_html, temp_pdf],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            end_time = time.time()
            
            duration = end_time - start_time
            
            if result.returncode == 0 and os.path.exists(temp_pdf):
                pdf_size = os.path.getsize(temp_pdf) / 1024  # KB
                self.log_result("性能基准测试", True, f"转换耗时: {duration:.2f}秒, PDF大小: {pdf_size:.1f}KB")
                
                # 性能评估
                if duration < 5:
                    performance_level = "优秀"
                elif duration < 15:
                    performance_level = "良好"
                elif duration < 30:
                    performance_level = "一般"
                else:
                    performance_level = "较差"
                    
                self.log_result("性能等级评估", True, performance_level)
            else:
                error_msg = result.stderr.strip() or f"返回码: {result.returncode}"
                self.log_result("性能基准测试", False, error_msg)
                duration = -1
            
            self._cleanup_temp_files([temp_html, temp_pdf])
            return duration > 0 and duration < 60
            
        except subprocess.TimeoutExpired:
            self.log_result("性能基准测试", False, "转换超时 (>60秒)")
            self._cleanup_temp_files([temp_html, temp_pdf])
            return False
        except Exception as e:
            self.log_result("性能基准测试", False, f"测试异常: {str(e)}")
            self._cleanup_temp_files([temp_html, temp_pdf])
            return False
    
    # === 综合测试管理 ===
    
    def run_all_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """运行所有测试并生成报告"""
        print("=" * 70)
        print("🚀 开始wkhtmltopdf综合完整性测试")
        print("=" * 70)
        
        self.start_time = datetime.now()
        
        # 定义测试顺序和权重
        test_suite = [
            (self.test_system_information, 10),
            (self.test_basic_installation, 15),
            (self.test_file_integrity, 10),
            (self.test_version_information, 10),
            (self.test_help_documentation, 5),
            (self.test_simple_html_conversion, 15),
            (self.test_complex_html_conversion, 20),
            (self.test_performance_benchmark, 15),
        ]
        
        passed_tests = 0
        total_weight = sum(weight for _, weight in test_suite)
        earned_points = 0
        
        for test_func, weight in test_suite:
            try:
                if test_func():
                    passed_tests += 1
                    earned_points += weight
            except Exception as e:
                test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_result(test_name, False, f"测试执行异常: {str(e)}")
        
        # 计算测试统计
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        success_rate = (passed_tests / len(test_suite)) * 100 if test_suite else 0
        score_percentage = (earned_points / total_weight) * 100 if total_weight > 0 else 0
        
        # 生成详细报告
        report = {
            'summary': {
                'total_tests': len(test_suite),
                'passed_tests': passed_tests,
                'failed_tests': len(test_suite) - passed_tests,
                'success_rate': success_rate,
                'score_percentage': score_percentage,
                'duration_seconds': duration,
                'timestamp': end_time.isoformat(),
            },
            'environment': {
                'wkhtmltopdf_path': self.wkhtmltopdf_path,
                'system_info': f"{platform.system()} {platform.release()}",
                'python_version': platform.python_version(),
            },
            'detailed_results': self.test_results
        }
        
        return score_percentage >= 70, report  # 70分以上视为通过
    
    def print_detailed_report(self, report: Dict[str, Any]):
        """打印详细的测试报告"""
        print("\n" + "=" * 70)
        print("📊 wkhtmltopdf综合测试报告")
        print("=" * 70)
        
        # 基本信息
        summary = report['summary']
        print(f"📅 测试时间: {summary['timestamp']}")
        print(f"⏱️  总耗时: {summary['duration_seconds']:.2f}秒")
        print(f"🎯 测试得分: {summary['score_percentage']:.1f}/100分")
        
        # 环境信息
        env = report['environment']
        print(f"\n🖥️  环境信息:")
        print(f"   系统: {env['system_info']}")
        print(f"   Python: {env['python_version']}")
        if env['wkhtmltopdf_path']:
            print(f"   wkhtmltopdf: {env['wkhtmltopdf_path']}")
        else:
            print(f"   wkhtmltopdf: 未找到")
        
        # 测试结果统计
        print(f"\n📈 测试统计:")
        print(f"   总测试项: {summary['total_tests']}")
        print(f"   通过项: {summary['passed_tests']}")
        print(f"   失败项: {summary['failed_tests']}")
        print(f"   通过率: {summary['success_rate']:.1f}%")
        
        # 详细结果
        print(f"\n📝 详细测试结果:")
        for result in report['detailed_results']:
            symbol = "✅" if result['success'] else "❌"
            severity_symbol = {
                'pass': '',
                'fail': '',
                'warn': ' ⚠️',
                'info': ' ℹ️'
            }.get(result['severity'], '')
            
            msg = f"  {symbol} {result['name']}{severity_symbol}"
            if result['message']:
                msg += f" - {result['message']}"
            print(msg)
        
        # 最终评估
        print("\n" + "=" * 70)
        score = summary['score_percentage']
        if score >= 90:
            print("🏆 优秀！wkhtmltopdf安装完整，功能齐全")
        elif score >= 70:
            print("👍 良好！wkhtmltopdf基本功能正常")
        elif score >= 50:
            print("⚠️  一般！部分功能可能存在问题")
        else:
            print("💥 较差！建议重新安装wkhtmltopdf")
        print("=" * 70)


def main():
    """主函数"""
    tester = WkhtmltopdfComprehensiveTester()
    
    try:
        success, report = tester.run_all_tests()
        tester.print_detailed_report(report)
        
        # 返回适当的退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 测试执行过程中发生严重错误: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    main()