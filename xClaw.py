#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
            "几乎涵盖了所有终端命令\n\n"
            "告别晦涩难懂，帮你轻松驾驭龙虾!\n"
            "支持 Gateway、渠道、配置、定时任务、\n"
            "配对、消息、插件、安全检查等功能管理\n\n"
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import json
import os
import re
import hashlib
import base64
from datetime import datetime
from typing import Optional, Dict, List, Callable

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")


class _OEMProtect:
    
    
    _K1 = [0x58, 0x43, 0x4C, 0x41, 0x57]
    _K2 = [0x4C, 0x4F, 0x42, 0x53, 0x54, 0x45, 0x52]
    
    _D = {
        'b': 'IAAgICB4bmyo6cGr1f++xeGq3Og=',
        'a': 'qsXUusv2EqX007bY07XWy6rl0aLo66rn5bPN6g==',
        's': 'aHR0cDovL3hobm9vYi5naXRodWIuaW8=',
        'at': 'IAAgICB4bmyo6cGr1f++xeGq3Og=',
    }
    
    _SIG = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    @classmethod
    def _x(cls, d: bytes, k: list) -> bytes:
        return bytes([b ^ k[i % len(k)] for i, b in enumerate(d)])
    
    @classmethod
    def _d(cls, e: str, k: list) -> str:
        try:
            r = base64.b64decode(e)
            return cls._x(r, k).decode('utf-8')
        except:
            return ""
    
    @classmethod
    def _r(cls, e: str) -> str:
        try:
            return base64.b64decode(e).decode('utf-8')
        except:
            return ""
    
    @classmethod
    def get_brand(cls) -> str:
        return cls._d(cls._D['b'], cls._K1)
    
    @classmethod
    def get_author(cls) -> str:
        return cls._d(cls._D['a'], cls._K2)
    
    @classmethod
    def get_site(cls) -> str:
        return cls._r(cls._D['s'])
    
    @classmethod
    def get_title(cls) -> str:
        return f"{cls.get_brand()} - {cls.get_author()}"
    
    @classmethod
    def get_about_title(cls) -> str:
        return f"关于{cls._d(cls._D['at'], cls._K1)}"
    
    @classmethod
    def get_welcome(cls) -> str:
        return f"{cls.get_brand()}\n\n - 几乎涵盖了所有终端命令，帮你轻松驾驭龙虾！\n\n{cls.get_author()}\n温馨提示：请谨慎使用本工具，造成的一切后果自行承担！"
    
    @classmethod
    def get_about_content(cls) -> str:
        return (
            f"{cls.get_brand()} v1.0\n\n"
            "几乎涵盖了所有终端命令\n\n"
            "告别晦涩难懂，帮你轻松驾驭龙虾!\n"
            "支持 Gateway、渠道、配置、定时任务、\n"
            "配对、消息、插件、安全检查等功能管理\n\n"
            f"作者：{cls.get_author()}\n"
            f"个站：{cls.get_site()}\n"
            "本工具造成的任何后果请自行承担！\n\n"
            "官网: https://docs.openclaw.ai/"
        )
    
    @classmethod
    def verify(cls) -> bool:
        try:
            _ = cls.get_brand()
            _ = cls.get_author()
            return True
        except:
            return False


def _get_oem():
    return _OEMProtect


class OpenClawCLI:
    """OpenClaw CLI 命令执行器"""

    def __init__(self, output_callback: Optional[Callable] = None):
        self.output_callback = output_callback
        self.running_process = None

    def run_command(self, command: str, capture: bool = True) -> tuple:
        """执行 openclaw 命令"""
        full_command = f"openclaw {command}"
        try:
            if capture:
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                output = result.stdout + result.stderr
                if self.output_callback:
                    self.output_callback(output)
                return result.returncode, output
            else:
                self.running_process = subprocess.Popen(
                    full_command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                return 0, ""
        except Exception as e:
            error_msg = f"执行命令失败: {str(e)}"
            if self.output_callback:
                self.output_callback(error_msg)
            return -1, error_msg

    def run_async(self, command: str, callback: Callable):
        """异步执行命令"""
        def _run():
            returncode, output = self.run_command(command)
            callback(returncode, output)
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread


class GatewayTab(ttk.Frame):
    """Gateway 管理标签页"""

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.LabelFrame(main_frame, text="Gateway 状态", padding="10")
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(status_frame, text="未检测", font=('Arial', 12))
        self.status_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(status_frame, text="刷新状态", command=self.refresh_status).pack(side=tk.RIGHT)

        control_frame = ttk.LabelFrame(main_frame, text="服务控制", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()

        ttk.Button(btn_frame, text="启动服务", command=self.start_gateway, width=12).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="停止服务", command=self.stop_gateway, width=12).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="重启服务", command=self.restart_gateway, width=12).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="前台运行", command=self.run_gateway, width=12).grid(row=0, column=3, padx=5, pady=5)

        service_frame = ttk.LabelFrame(main_frame, text="系统服务", padding="10")
        service_frame.pack(fill=tk.X, pady=5)

        btn_frame2 = ttk.Frame(service_frame)
        btn_frame2.pack()

        ttk.Button(btn_frame2, text="安装服务", command=self.install_service, width=12).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame2, text="卸载服务", command=self.uninstall_service, width=12).grid(row=0, column=1, padx=5, pady=5)

        options_frame = ttk.LabelFrame(main_frame, text="启动选项", padding="10")
        options_frame.pack(fill=tk.X, pady=5)

        opt_row = ttk.Frame(options_frame)
        opt_row.pack(fill=tk.X)

        ttk.Label(opt_row, text="端口:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar(value="18789")
        ttk.Entry(opt_row, textvariable=self.port_var, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Label(opt_row, text="绑定:").pack(side=tk.LEFT, padx=5)
        self.bind_var = tk.StringVar(value="loopback")
        bind_combo = ttk.Combobox(opt_row, textvariable=self.bind_var, values=["loopback", "lan", "tailnet"], width=10, state="readonly")
        bind_combo.pack(side=tk.LEFT, padx=5)

        self.force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row, text="强制启动", variable=self.force_var).pack(side=tk.LEFT, padx=10)

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_row, text="详细日志", variable=self.verbose_var).pack(side=tk.LEFT, padx=10)

        log_frame = ttk.LabelFrame(main_frame, text="实时日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self._show_welcome_message()

        btn_row = ttk.Frame(log_frame)
        btn_row.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row, text="查看实时日志", command=self.view_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="Gateway诊断", command=self.probe_gateway).pack(side=tk.LEFT, padx=5)

    def log(self, message: str):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _show_welcome_message(self):
        oem = _get_oem()
        welcome_msg = oem.get_welcome()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, welcome_msg + "\n")
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def refresh_status(self):
        self.log("正在获取 Gateway 状态...")
        def callback(code, output):
            self.status_label.config(text=output.strip() if output.strip() else "未知状态")
            self.log(output)
        self.cli.run_async("gateway status", callback)

    def start_gateway(self):
        options = self._build_options()
        self.log(f"正在启动 Gateway... {options}")
        def callback(code, output):
            self.log(output)
            if code == 0:
                self.status_label.config(text="运行中")
        self.cli.run_async(f"gateway start {options}", callback)

    def stop_gateway(self):
        self.log("正在停止 Gateway...")
        def callback(code, output):
            self.log(output)
            self.status_label.config(text="已停止")
        self.cli.run_async("gateway stop", callback)

    def restart_gateway(self):
        self.log("正在重启 Gateway...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("gateway restart", callback)

    def run_gateway(self):
        options = self._build_options()
        self.log(f"前台运行 Gateway... {options}")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"gateway run {options}", callback)

    def install_service(self):
        self.log("正在安装系统服务...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("gateway install", callback)

    def uninstall_service(self):
        self.log("正在卸载系统服务...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("gateway uninstall", callback)

    def view_logs(self):
        self.log("获取实时日志...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("logs --follow", callback)

    def probe_gateway(self):
        self.log("执行 Gateway 诊断...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("gateway probe", callback)

    def _build_options(self) -> str:
        options = []
        if self.port_var.get():
            options.append(f"--port {self.port_var.get()}")
        if self.bind_var.get():
            options.append(f"--bind {self.bind_var.get()}")
        if self.force_var.get():
            options.append("--force")
        if self.verbose_var.get():
            options.append("--verbose")
        return " ".join(options)


class ChannelsTab(ttk.Frame):
    """渠道管理标签页"""

    CHANNELS = ["feishu", "telegram", "whatsapp", "discord", "slack", "signal", "imessage", "googlechat", "matrix", "irc", "nostr"]

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.LabelFrame(main_frame, text="已配置渠道", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("渠道", "状态", "启用")
        self.channels_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.channels_tree.heading(col, text=col)
            self.channels_tree.column(col, width=100)
        self.channels_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="刷新列表", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查看状态", command=self.view_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查看日志", command=self.view_logs).pack(side=tk.LEFT, padx=5)

        add_frame = ttk.LabelFrame(main_frame, text="添加渠道", padding="10")
        add_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(add_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="渠道类型:").pack(side=tk.LEFT, padx=5)
        self.channel_var = tk.StringVar()
        ttk.Combobox(row1, textvariable=self.channel_var, values=self.CHANNELS, width=15, state="readonly").pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(add_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Token:").pack(side=tk.LEFT, padx=5)
        self.token_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.token_var, width=40).pack(side=tk.LEFT, padx=5)

        btn_row = ttk.Frame(add_frame)
        btn_row.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row, text="添加渠道", command=self.add_channel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="登录渠道", command=self.login_channel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="登出渠道", command=self.logout_channel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="移除渠道", command=self.remove_channel).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.LabelFrame(main_frame, text="输出", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def refresh_list(self):
        self.log("正在获取渠道列表...")
        def callback(code, output):
            self.log(output)
            self._parse_channels(output)
        self.cli.run_async("channels list", callback)

    def _parse_channels(self, output: str):
        self.channels_tree.delete(*self.channels_tree.get_children())
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('List') and not line.startswith('==='):
                parts = line.split()
                if len(parts) >= 1:
                    channel = parts[0]
                    status = parts[1] if len(parts) > 1 else "未知"
                    enabled = parts[2] if len(parts) > 2 else "是"
                    self.channels_tree.insert("", tk.END, values=(channel, status, enabled))

    def view_status(self):
        self.log("正在获取渠道状态...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("channels status", callback)

    def view_logs(self):
        self.log("正在获取渠道日志...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("channels logs", callback)

    def add_channel(self):
        channel = self.channel_var.get()
        token = self.token_var.get()
        if not channel:
            messagebox.showwarning("警告", "请选择渠道类型")
            return
        cmd = f"channels add --channel {channel}"
        if token:
            cmd += f" --token {token}"
        self.log(f"正在添加渠道: {channel}...")
        def callback(code, output):
            self.log(output)
            self.refresh_list()
        self.cli.run_async(cmd, callback)

    def login_channel(self):
        channel = self.channel_var.get()
        if not channel:
            messagebox.showwarning("警告", "请选择渠道类型")
            return
        self.log(f"正在登录渠道: {channel}...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"channels login --channel {channel}", callback)

    def logout_channel(self):
        channel = self.channel_var.get()
        if not channel:
            messagebox.showwarning("警告", "请选择渠道类型")
            return
        self.log(f"正在登出渠道: {channel}...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"channels logout --channel {channel}", callback)

    def remove_channel(self):
        channel = self.channel_var.get()
        if not channel:
            messagebox.showwarning("警告", "请选择渠道类型")
            return
        if messagebox.askyesno("确认", f"确定要移除渠道 {channel} 吗?"):
            self.log(f"正在移除渠道: {channel}...")
            def callback(code, output):
                self.log(output)
                self.refresh_list()
            self.cli.run_async(f"channels remove --channel {channel}", callback)


class ConfigTab(ttk.Frame):
    """配置管理标签页"""

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.config_data = {}
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="配置路径:").pack(anchor=tk.W, padx=5)
        self.path_label = ttk.Label(left_frame, text=CONFIG_PATH, foreground="blue")
        self.path_label.pack(anchor=tk.W, padx=5, pady=2)

        ttk.Button(left_frame, text="加载配置", command=self.load_config).pack(anchor=tk.W, padx=5, pady=5)
        ttk.Button(left_frame, text="保存配置", command=self.save_config).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Button(left_frame, text="重新加载", command=self.reload_config).pack(anchor=tk.W, padx=5, pady=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(left_frame, text="配置键 (如: channels.feishu.enabled):").pack(anchor=tk.W, padx=5)
        self.key_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.key_var, width=40).pack(anchor=tk.W, padx=5, pady=2)

        ttk.Label(left_frame, text="配置值:").pack(anchor=tk.W, padx=5)
        self.value_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.value_var, width=40).pack(anchor=tk.W, padx=5, pady=2)

        btn_row = ttk.Frame(left_frame)
        btn_row.pack(anchor=tk.W, pady=5)
        ttk.Button(btn_row, text="获取", command=self.get_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="设置", command=self.set_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="删除", command=self.unset_config).pack(side=tk.LEFT, padx=5)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(left_frame, text="快速设置:").pack(anchor=tk.W, padx=5)
        quick_frame = ttk.Frame(left_frame)
        quick_frame.pack(anchor=tk.W, padx=5, pady=5)

        ttk.Label(quick_frame, text="主模型:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.model_var, width=30).grid(row=0, column=1, pady=2)
        ttk.Button(quick_frame, text="设置", command=self.set_model).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(quick_frame, text="Gateway端口:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.gw_port_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.gw_port_var, width=30).grid(row=1, column=1, pady=2)
        ttk.Button(quick_frame, text="设置", command=self.set_port).grid(row=1, column=2, padx=5, pady=2)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="配置内容 (JSON):").pack(anchor=tk.W, padx=5)
        self.config_text = scrolledtext.ScrolledText(right_frame, height=20)
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(tk.END, json.dumps(self.config_data, indent=2, ensure_ascii=False))
            messagebox.showinfo("成功", "配置加载成功")
        except FileNotFoundError:
            messagebox.showerror("错误", f"配置文件不存在: {CONFIG_PATH}")
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON 解析错误: {e}")

    def save_config(self):
        try:
            content = self.config_text.get(1.0, tk.END)
            self.config_data = json.loads(content)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "配置保存成功")
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON 格式错误: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def reload_config(self):
        self.load_config()

    def get_config(self):
        key = self.key_var.get()
        if not key:
            messagebox.showwarning("警告", "请输入配置键")
            return
        def callback(code, output):
            self.value_var.set(output.strip())
        self.cli.run_async(f"config get {key}", callback)

    def set_config(self):
        key = self.key_var.get()
        value = self.value_var.get()
        if not key:
            messagebox.showwarning("警告", "请输入配置键")
            return
        quoted_value = f'"{value}"' if not value.isdigit() and value not in ['true', 'false'] else value
        def callback(code, output):
            messagebox.showinfo("成功", f"配置已设置: {key} = {value}")
            self.load_config()
        self.cli.run_async(f'config set {key} {quoted_value}', callback)

    def unset_config(self):
        key = self.key_var.get()
        if not key:
            messagebox.showwarning("警告", "请输入配置键")
            return
        if messagebox.askyesno("确认", f"确定要删除配置 {key} 吗?"):
            def callback(code, output):
                messagebox.showinfo("成功", f"配置已删除: {key}")
                self.load_config()
            self.cli.run_async(f"config unset {key}", callback)

    def set_model(self):
        model = self.model_var.get()
        if not model:
            messagebox.showwarning("警告", "请输入模型名称")
            return
        self.key_var.set("agents.defaults.model.primary")
        self.value_var.set(model)
        self.set_config()

    def set_port(self):
        port = self.gw_port_var.get()
        if not port:
            messagebox.showwarning("警告", "请输入端口号")
            return
        self.key_var.set("gateway.port")
        self.value_var.set(port)
        self.set_config()


class CronTab(ttk.Frame):
    """定时任务管理标签页"""

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.LabelFrame(main_frame, text="定时任务列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("ID", "调度", "消息", "状态")
        self.cron_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col, width in zip(columns, [80, 150, 200, 80]):
            self.cron_tree.heading(col, text=col)
            self.cron_tree.column(col, width=width)
        self.cron_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="刷新列表", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查看历史", command=self.view_runs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="调度器状态", command=self.view_status).pack(side=tk.LEFT, padx=5)

        add_frame = ttk.LabelFrame(main_frame, text="添加定时任务", padding="10")
        add_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(add_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="调度表达式 (cron):").pack(side=tk.LEFT, padx=5)
        self.schedule_var = tk.StringVar(value="*/5 * * * *")
        ttk.Entry(row1, textvariable=self.schedule_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(row1, text="(分 时 日 月 周)").pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(add_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="消息内容:").pack(side=tk.LEFT, padx=5)
        self.message_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.message_var, width=50).pack(side=tk.LEFT, padx=5)

        btn_row = ttk.Frame(add_frame)
        btn_row.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row, text="添加任务", command=self.add_cron).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="立即运行", command=self.run_cron).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="启用", command=self.enable_cron).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="禁用", command=self.disable_cron).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="删除", command=self.remove_cron).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.LabelFrame(main_frame, text="输出", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=6, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def refresh_list(self):
        self.log("正在获取定时任务列表...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("cron list", callback)

    def view_runs(self):
        self.log("正在获取任务运行历史...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("cron runs", callback)

    def view_status(self):
        self.log("正在获取调度器状态...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("cron status", callback)

    def add_cron(self):
        schedule = self.schedule_var.get()
        message = self.message_var.get()
        if not schedule or not message:
            messagebox.showwarning("警告", "请填写调度表达式和消息内容")
            return
        self.log(f"正在添加定时任务: {schedule} - {message}")
        def callback(code, output):
            self.log(output)
            self.refresh_list()
        self.cli.run_async(f'cron add --schedule "{schedule}" --message "{message}"', callback)

    def run_cron(self):
        job_id = self._get_selected_id()
        if not job_id:
            messagebox.showwarning("警告", "请选择一个任务")
            return
        self.log(f"正在运行任务: {job_id}")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"cron run {job_id}", callback)

    def enable_cron(self):
        job_id = self._get_selected_id()
        if not job_id:
            messagebox.showwarning("警告", "请选择一个任务")
            return
        self.log(f"正在启用任务: {job_id}")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"cron enable {job_id}", callback)

    def disable_cron(self):
        job_id = self._get_selected_id()
        if not job_id:
            messagebox.showwarning("警告", "请选择一个任务")
            return
        self.log(f"正在禁用任务: {job_id}")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"cron disable {job_id}", callback)

    def remove_cron(self):
        job_id = self._get_selected_id()
        if not job_id:
            messagebox.showwarning("警告", "请选择一个任务")
            return
        if messagebox.askyesno("确认", f"确定要删除任务 {job_id} 吗?"):
            self.log(f"正在删除任务: {job_id}")
            def callback(code, output):
                self.log(output)
                self.refresh_list()
            self.cli.run_async(f"cron rm {job_id}", callback)

    def _get_selected_id(self) -> Optional[str]:
        selection = self.cron_tree.selection()
        if selection:
            item = self.cron_tree.item(selection[0])
            return item['values'][0] if item['values'] else None
        return None


class PairingTab(ttk.Frame):
    """配对与设备管理标签页"""

    CHANNELS = ["feishu", "telegram", "whatsapp", "signal", "imessage", "discord", "slack"]

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        pairing_frame = ttk.LabelFrame(main_frame, text="配对请求", padding="10")
        pairing_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("渠道", "代码", "状态")
        self.pairing_tree = ttk.Treeview(pairing_frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.pairing_tree.heading(col, text=col)
            self.pairing_tree.column(col, width=100)
        self.pairing_tree.pack(fill=tk.BOTH, expand=True)

        pair_btn_frame = ttk.Frame(pairing_frame)
        pair_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pair_btn_frame, text="渠道:").pack(side=tk.LEFT, padx=5)
        self.channel_var = tk.StringVar()
        ttk.Combobox(pair_btn_frame, textvariable=self.channel_var, values=self.CHANNELS, width=12, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(pair_btn_frame, text="代码:").pack(side=tk.LEFT, padx=5)
        self.code_var = tk.StringVar()
        ttk.Entry(pair_btn_frame, textvariable=self.code_var, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Button(pair_btn_frame, text="刷新列表", command=self.refresh_pairing).pack(side=tk.LEFT, padx=10)
        ttk.Button(pair_btn_frame, text="批准", command=self.approve_pairing).pack(side=tk.LEFT, padx=5)
        ttk.Button(pair_btn_frame, text="拒绝", command=self.reject_pairing).pack(side=tk.LEFT, padx=5)

        devices_frame = ttk.LabelFrame(main_frame, text="设备管理", padding="10")
        devices_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns2 = ("ID", "名称", "状态")
        self.devices_tree = ttk.Treeview(devices_frame, columns=columns2, show="headings", height=6)
        for col in columns2:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=100)
        self.devices_tree.pack(fill=tk.BOTH, expand=True)

        dev_btn_frame = ttk.Frame(devices_frame)
        dev_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(dev_btn_frame, text="刷新设备", command=self.refresh_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(dev_btn_frame, text="批准设备", command=self.approve_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(dev_btn_frame, text="拒绝设备", command=self.reject_device).pack(side=tk.LEFT, padx=5)

        nodes_frame = ttk.LabelFrame(main_frame, text="节点管理", padding="10")
        nodes_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns3 = ("节点ID", "状态", "位置")
        self.nodes_tree = ttk.Treeview(nodes_frame, columns=columns3, show="headings", height=5)
        for col in columns3:
            self.nodes_tree.heading(col, text=col)
            self.nodes_tree.column(col, width=100)
        self.nodes_tree.pack(fill=tk.BOTH, expand=True)

        node_btn_frame = ttk.Frame(nodes_frame)
        node_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(node_btn_frame, text="刷新节点", command=self.refresh_nodes).pack(side=tk.LEFT, padx=5)
        ttk.Button(node_btn_frame, text="待配对节点", command=self.pending_nodes).pack(side=tk.LEFT, padx=5)
        ttk.Button(node_btn_frame, text="批准节点", command=self.approve_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(node_btn_frame, text="获取截屏", command=self.node_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(node_btn_frame, text="获取照片", command=self.node_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(node_btn_frame, text="获取位置", command=self.node_location).pack(side=tk.LEFT, padx=5)

    def refresh_pairing(self):
        channel = self.channel_var.get()
        cmd = f"pairing list {channel}" if channel else "pairing list"
        def callback(code, output):
            pass
        self.cli.run_async(cmd, callback)

    def approve_pairing(self):
        channel = self.channel_var.get()
        code = self.code_var.get()
        if not channel or not code:
            messagebox.showwarning("警告", "请选择渠道并输入代码")
            return
        def callback(code, output):
            self.refresh_pairing()
        self.cli.run_async(f"pairing approve {channel} {code}", callback)

    def reject_pairing(self):
        channel = self.channel_var.get()
        code = self.code_var.get()
        if not channel or not code:
            messagebox.showwarning("警告", "请选择渠道并输入代码")
            return
        def callback(code, output):
            self.refresh_pairing()
        self.cli.run_async(f"pairing reject {channel} {code}", callback)

    def refresh_devices(self):
        def callback(code, output):
            pass
        self.cli.run_async("devices list", callback)

    def approve_device(self):
        request_id = self._get_device_id()
        if not request_id:
            messagebox.showwarning("警告", "请选择一个设备")
            return
        def callback(code, output):
            self.refresh_devices()
        self.cli.run_async(f"devices approve {request_id}", callback)

    def reject_device(self):
        request_id = self._get_device_id()
        if not request_id:
            messagebox.showwarning("警告", "请选择一个设备")
            return
        def callback(code, output):
            self.refresh_devices()
        self.cli.run_async(f"devices reject {request_id}", callback)

    def refresh_nodes(self):
        def callback(code, output):
            pass
        self.cli.run_async("nodes status", callback)

    def pending_nodes(self):
        def callback(code, output):
            pass
        self.cli.run_async("nodes pending", callback)

    def approve_node(self):
        node_id = self._get_node_id()
        if not node_id:
            messagebox.showwarning("警告", "请选择一个节点")
            return
        def callback(code, output):
            self.refresh_nodes()
        self.cli.run_async(f"nodes approve {node_id}", callback)

    def node_screen(self):
        node_id = self._get_node_id()
        if not node_id:
            messagebox.showwarning("警告", "请选择一个节点")
            return
        def callback(code, output):
            pass
        self.cli.run_async(f"nodes screen snap --node {node_id}", callback)

    def node_camera(self):
        node_id = self._get_node_id()
        if not node_id:
            messagebox.showwarning("警告", "请选择一个节点")
            return
        def callback(code, output):
            pass
        self.cli.run_async(f"nodes camera snap --node {node_id}", callback)

    def node_location(self):
        node_id = self._get_node_id()
        if not node_id:
            messagebox.showwarning("警告", "请选择一个节点")
            return
        def callback(code, output):
            pass
        self.cli.run_async(f"nodes location --node {node_id}", callback)

    def _get_device_id(self) -> Optional[str]:
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            return item['values'][0] if item['values'] else None
        return None

    def _get_node_id(self) -> Optional[str]:
        selection = self.nodes_tree.selection()
        if selection:
            item = self.nodes_tree.item(selection[0])
            return item['values'][0] if item['values'] else None
        return None


class MessageTab(ttk.Frame):
    """消息发送标签页"""

    CHANNELS = ["feishu", "telegram", "whatsapp", "discord", "slack", "signal", "imessage"]

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        send_frame = ttk.LabelFrame(main_frame, text="发送消息", padding="10")
        send_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(send_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="渠道:").pack(side=tk.LEFT, padx=5)
        self.channel_var = tk.StringVar()
        ttk.Combobox(row1, textvariable=self.channel_var, values=self.CHANNELS, width=15, state="readonly").pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="目标:").pack(side=tk.LEFT, padx=5)
        self.target_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.target_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Label(row1, text="(用户ID或@用户名)").pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(send_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="消息:").pack(side=tk.LEFT, padx=5)
        self.message_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.message_var, width=60).pack(side=tk.LEFT, padx=5)

        row3 = ttk.Frame(send_frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Label(row3, text="图片:").pack(side=tk.LEFT, padx=5)
        self.image_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.image_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="浏览...", command=self.browse_image).pack(side=tk.LEFT, padx=5)

        btn_row = ttk.Frame(send_frame)
        btn_row.pack(fill=tk.X, pady=10)
        ttk.Button(btn_row, text="发送消息", command=self.send_message, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_row, text="发送图片", command=self.send_image, width=15).pack(side=tk.LEFT, padx=10)

        history_frame = ttk.LabelFrame(main_frame, text="消息历史", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        hist_row = ttk.Frame(history_frame)
        hist_row.pack(fill=tk.X, pady=5)
        ttk.Label(hist_row, text="会话Key:").pack(side=tk.LEFT, padx=5)
        self.session_var = tk.StringVar()
        ttk.Entry(hist_row, textvariable=self.session_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(hist_row, text="查看历史", command=self.view_history).pack(side=tk.LEFT, padx=10)

        self.history_text = scrolledtext.ScrolledText(history_frame, height=10, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True)

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.image_var.set(file_path)

    def send_message(self):
        channel = self.channel_var.get()
        target = self.target_var.get()
        message = self.message_var.get()
        if not channel or not target or not message:
            messagebox.showwarning("警告", "请填写渠道、目标和消息内容")
            return
        def callback(code, output):
            self._log_history(f"发送到 {channel}/{target}: {message}")
            self._log_history(output)
        self.cli.run_async(f'message send --channel {channel} --target "{target}" --message "{message}"', callback)

    def send_image(self):
        channel = self.channel_var.get()
        target = self.target_var.get()
        image = self.image_var.get()
        if not channel or not target or not image:
            messagebox.showwarning("警告", "请填写渠道、目标和图片路径")
            return
        def callback(code, output):
            self._log_history(f"发送图片到 {channel}/{target}: {image}")
            self._log_history(output)
        self.cli.run_async(f'message send --channel {channel} --target "{target}" --image "{image}"', callback)

    def view_history(self):
        session = self.session_var.get()
        if not session:
            messagebox.showwarning("警告", "请输入会话Key")
            return
        def callback(code, output):
            self._log_history(output)
        self.cli.run_async(f"message history --session {session}", callback)

    def _log_history(self, message: str):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{message}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)


class PluginsTab(ttk.Frame):
    """插件与代理管理标签页"""

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        plugins_frame = ttk.LabelFrame(main_frame, text="插件管理", padding="10")
        plugins_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("名称", "版本", "状态")
        self.plugins_tree = ttk.Treeview(plugins_frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.plugins_tree.heading(col, text=col)
            self.plugins_tree.column(col, width=100)
        self.plugins_tree.pack(fill=tk.BOTH, expand=True)

        plug_btn_frame = ttk.Frame(plugins_frame)
        plug_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(plug_btn_frame, text="刷新列表", command=self.refresh_plugins).pack(side=tk.LEFT, padx=5)

        ttk.Label(plug_btn_frame, text="插件名:").pack(side=tk.LEFT, padx=10)
        self.plugin_var = tk.StringVar()
        ttk.Entry(plug_btn_frame, textvariable=self.plugin_var, width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(plug_btn_frame, text="安装", command=self.install_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(plug_btn_frame, text="卸载", command=self.uninstall_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(plug_btn_frame, text="启用", command=self.enable_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(plug_btn_frame, text="禁用", command=self.disable_plugin).pack(side=tk.LEFT, padx=5)

        agents_frame = ttk.LabelFrame(main_frame, text="代理管理", padding="10")
        agents_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns2 = ("ID", "模型", "状态")
        self.agents_tree = ttk.Treeview(agents_frame, columns=columns2, show="headings", height=6)
        for col in columns2:
            self.agents_tree.heading(col, text=col)
            self.agents_tree.column(col, width=100)
        self.agents_tree.pack(fill=tk.BOTH, expand=True)

        agent_btn_frame = ttk.Frame(agents_frame)
        agent_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(agent_btn_frame, text="刷新列表", command=self.refresh_agents).pack(side=tk.LEFT, padx=5)
        ttk.Button(agent_btn_frame, text="创建代理", command=self.create_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(agent_btn_frame, text="删除代理", command=self.remove_agent).pack(side=tk.LEFT, padx=5)

        interact_frame = ttk.LabelFrame(main_frame, text="快速交互", padding="10")
        interact_frame.pack(fill=tk.X, pady=5)

        int_row = ttk.Frame(interact_frame)
        int_row.pack(fill=tk.X, pady=5)
        ttk.Label(int_row, text="消息:").pack(side=tk.LEFT, padx=5)
        self.agent_msg_var = tk.StringVar()
        ttk.Entry(int_row, textvariable=self.agent_msg_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(int_row, text="发送", command=self.send_to_agent).pack(side=tk.LEFT, padx=10)

        output_frame = ttk.LabelFrame(main_frame, text="输出", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=6, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def refresh_plugins(self):
        self.log("正在获取插件列表...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("plugins list", callback)

    def install_plugin(self):
        plugin = self.plugin_var.get()
        if not plugin:
            messagebox.showwarning("警告", "请输入插件名称")
            return
        self.log(f"正在安装插件: {plugin}")
        def callback(code, output):
            self.log(output)
            self.refresh_plugins()
        self.cli.run_async(f"plugins install {plugin}", callback)

    def uninstall_plugin(self):
        plugin = self.plugin_var.get()
        if not plugin:
            messagebox.showwarning("警告", "请输入插件名称")
            return
        if messagebox.askyesno("确认", f"确定要卸载插件 {plugin} 吗?"):
            self.log(f"正在卸载插件: {plugin}")
            def callback(code, output):
                self.log(output)
                self.refresh_plugins()
            self.cli.run_async(f"plugins uninstall {plugin}", callback)

    def enable_plugin(self):
        plugin = self.plugin_var.get()
        if not plugin:
            messagebox.showwarning("警告", "请输入插件名称")
            return
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"plugins enable {plugin}", callback)

    def disable_plugin(self):
        plugin = self.plugin_var.get()
        if not plugin:
            messagebox.showwarning("警告", "请输入插件名称")
            return
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f"plugins disable {plugin}", callback)

    def refresh_agents(self):
        self.log("正在获取代理列表...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("agents list", callback)

    def create_agent(self):
        self.log("正在创建代理...")
        def callback(code, output):
            self.log(output)
            self.refresh_agents()
        self.cli.run_async("agents create", callback)

    def remove_agent(self):
        agent_id = self._get_agent_id()
        if not agent_id:
            messagebox.showwarning("警告", "请选择一个代理")
            return
        if messagebox.askyesno("确认", f"确定要删除代理 {agent_id} 吗?"):
            self.log(f"正在删除代理: {agent_id}")
            def callback(code, output):
                self.log(output)
                self.refresh_agents()
            self.cli.run_async(f"agents remove {agent_id}", callback)

    def send_to_agent(self):
        message = self.agent_msg_var.get()
        if not message:
            messagebox.showwarning("警告", "请输入消息内容")
            return
        self.log(f"发送消息到代理: {message}")
        def callback(code, output):
            self.log(output)
        self.cli.run_async(f'agent --message "{message}"', callback)

    def _get_agent_id(self) -> Optional[str]:
        selection = self.agents_tree.selection()
        if selection:
            item = self.agents_tree.item(selection[0])
            return item['values'][0] if item['values'] else None
        return None


class SecurityTab(ttk.Frame):
    """安全检查与工具标签页"""

    def __init__(self, parent, cli: OpenClawCLI):
        super().__init__(parent)
        self.cli = cli
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        health_frame = ttk.LabelFrame(main_frame, text="健康检查", padding="10")
        health_frame.pack(fill=tk.X, pady=5)

        btn_row1 = ttk.Frame(health_frame)
        btn_row1.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row1, text="运行健康检查", command=self.run_doctor, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="非交互式检查", command=self.run_doctor_nonint, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="查看状态", command=self.view_status, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="深度检查", command=self.view_status_deep, width=15).pack(side=tk.LEFT, padx=5)

        security_frame = ttk.LabelFrame(main_frame, text="安全审计", padding="10")
        security_frame.pack(fill=tk.X, pady=5)

        btn_row2 = ttk.Frame(security_frame)
        btn_row2.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row2, text="安全审计", command=self.security_audit, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row2, text="深度审计", command=self.security_audit_deep, width=15).pack(side=tk.LEFT, padx=5)

        tools_frame = ttk.LabelFrame(main_frame, text="实用工具", padding="10")
        tools_frame.pack(fill=tk.X, pady=5)

        btn_row3 = ttk.Frame(tools_frame)
        btn_row3.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row3, text="查看版本", command=self.view_version, width=12).grid(row=0, column=0, padx=5, pady=3)
        ttk.Button(btn_row3, text="查看模型", command=self.view_models, width=12).grid(row=0, column=1, padx=5, pady=3)
        ttk.Button(btn_row3, text="查看技能", command=self.view_skills, width=12).grid(row=0, column=2, padx=5, pady=3)
        ttk.Button(btn_row3, text="查看文档", command=self.view_docs, width=12).grid(row=0, column=3, padx=5, pady=3)
        ttk.Button(btn_row3, text="搜索记忆", command=self.search_memory, width=12).grid(row=0, column=4, padx=5, pady=3)

        update_frame = ttk.LabelFrame(main_frame, text="更新管理", padding="10")
        update_frame.pack(fill=tk.X, pady=5)

        btn_row4 = ttk.Frame(update_frame)
        btn_row4.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row4, text="检查更新", command=self.check_update, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row4, text="执行更新", command=self.run_update, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row4, text="重置配置", command=self.reset_config, width=12).pack(side=tk.LEFT, padx=10)

        output_frame = ttk.LabelFrame(main_frame, text="输出", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=12, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        btn_row5 = ttk.Frame(output_frame)
        btn_row5.pack(fill=tk.X, pady=5)
        ttk.Button(btn_row5, text="清空输出", command=self.clear_output).pack(side=tk.LEFT, padx=5)

    def log(self, message: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def run_doctor(self):
        self.log("运行健康检查...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("doctor", callback)

    def run_doctor_nonint(self):
        self.log("运行非交互式健康检查...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("doctor --non-interactive", callback)

    def view_status(self):
        self.log("获取系统状态...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("status", callback)

    def view_status_deep(self):
        self.log("获取深度状态...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("status --deep", callback)

    def security_audit(self):
        self.log("运行安全审计...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("security audit", callback)

    def security_audit_deep(self):
        self.log("运行深度安全审计...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("security audit --deep", callback)

    def view_version(self):
        def callback(code, output):
            self.log(output)
        self.cli.run_async("--version", callback)

    def view_models(self):
        self.log("获取模型列表...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("models list", callback)

    def view_skills(self):
        self.log("获取技能列表...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("skills list", callback)

    def view_docs(self):
        query = self._ask_input("搜索文档", "请输入搜索关键词:")
        if query:
            self.log(f"搜索文档: {query}")
            def callback(code, output):
                self.log(output)
            self.cli.run_async(f"docs {query}", callback)

    def search_memory(self):
        query = self._ask_input("搜索记忆", "请输入搜索关键词:")
        if query:
            self.log(f"搜索记忆: {query}")
            def callback(code, output):
                self.log(output)
            self.cli.run_async(f"memory search {query}", callback)

    def check_update(self):
        self.log("检查更新...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("update status", callback)

    def run_update(self):
        self.log("执行更新...")
        def callback(code, output):
            self.log(output)
        self.cli.run_async("update run", callback)

    def reset_config(self):
        if messagebox.askyesno("确认", "确定要重置配置吗? 这将保留 CLI 但清除其他配置。"):
            self.log("重置配置...")
            def callback(code, output):
                self.log(output)
            self.cli.run_async("reset", callback)

    def _ask_input(self, title: str, prompt: str) -> Optional[str]:
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("300x100")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        result = [None]
        ttk.Label(dialog, text=prompt).pack(pady=10)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)

        def on_ok(event=None):
            result[0] = entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        entry.bind("<Return>", on_ok)
        ttk.Button(dialog, text="确定", command=on_ok).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(dialog, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=20, pady=10)

        dialog.wait_window()
        return result[0]


class OpenClawGUI:
    """OpenClaw GUI 主窗口"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(_get_oem().get_title())
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self.cli = OpenClawCLI(self.output_callback)

        self.setup_styles()
        self.setup_menu()
        self.setup_ui()

        self.check_openclaw()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开配置文件", command=self.open_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="打开 Dashboard", command=self.open_dashboard)
        tools_menu.add_command(label="运行配置向导", command=self.run_configure)
        tools_menu.add_command(label="运行 Onboard", command=self.run_onboard)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="查看文档", command=self.view_docs)
        help_menu.add_command(label="关于", command=self.show_about)

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.gateway_tab = GatewayTab(self.notebook, self.cli)
        self.notebook.add(self.gateway_tab, text="Gateway 管理")

        self.channels_tab = ChannelsTab(self.notebook, self.cli)
        self.notebook.add(self.channels_tab, text="渠道管理")

        self.config_tab = ConfigTab(self.notebook, self.cli)
        self.notebook.add(self.config_tab, text="配置管理")

        self.cron_tab = CronTab(self.notebook, self.cli)
        self.notebook.add(self.cron_tab, text="定时任务")

        self.pairing_tab = PairingTab(self.notebook, self.cli)
        self.notebook.add(self.pairing_tab, text="配对设备")

        self.message_tab = MessageTab(self.notebook, self.cli)
        self.notebook.add(self.message_tab, text="消息发送")

        self.plugins_tab = PluginsTab(self.notebook, self.cli)
        self.notebook.add(self.plugins_tab, text="插件代理")

        self.security_tab = SecurityTab(self.notebook, self.cli)
        self.notebook.add(self.security_tab, text="安全工具")

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, padx=5, pady=2)

    def output_callback(self, output: str):
        pass

    def check_openclaw(self):
        try:
            result = subprocess.run("openclaw --version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.status_var.set(f"OpenClaw 已安装: {result.stdout.strip()}")
            else:
                self.status_var.set("OpenClaw 未找到，请确保已安装并添加到 PATH")
        except Exception:
            self.status_var.set("无法检测 OpenClaw")

    def open_config(self):
        if os.path.exists(CONFIG_PATH):
            os.startfile(CONFIG_PATH)
        else:
            messagebox.showinfo("提示", f"配置文件不存在: {CONFIG_PATH}")

    def open_dashboard(self):
        try:
            import webbrowser
            webbrowser.open("http://127.0.0.1:18789/")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 Dashboard: {e}")

    def run_configure(self):
        def callback(code, output):
            pass
        self.cli.run_async("configure", callback)

    def run_onboard(self):
        def callback(code, output):
            pass
        self.cli.run_async("onboard", callback)

    def view_docs(self):
        try:
            import webbrowser
            webbrowser.open("https://docs.openclaw.ai/")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文档: {e}")

    def show_about(self):
        oem = _get_oem()
        messagebox.showinfo(
            oem.get_about_title(),
            oem.get_about_content()
        )


def main():
    root = tk.Tk()
    app = OpenClawGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
