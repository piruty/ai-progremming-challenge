"""
メインウィンドウビュー
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinterdnd2 as tkdnd
from typing import Optional, Callable
from PIL import ImageTk

from models.settings import AppSettings


class MainWindow:
    """メインウィンドウのUIクラス"""
    
    def __init__(self, root: tk.Tk, settings: AppSettings):
        self.root = root
        self.settings = settings
        self.preview_image: Optional[ImageTk.PhotoImage] = None
        
        # コールバック関数
        self.on_file_select: Optional[Callable[[str], None]] = None
        self.on_drop: Optional[Callable[[str], None]] = None
        self.on_preview_update: Optional[Callable[[], None]] = None
        self.on_save: Optional[Callable[[], None]] = None
        self.on_save_as: Optional[Callable[[], None]] = None
        self.on_reset: Optional[Callable[[], None]] = None
        self.on_settings_change: Optional[Callable[[], None]] = None
        
        self.setup_window()
        self.setup_ui()
        self.setup_drag_drop()
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("画像リサイズ & 圧縮アプリ")
        width, height = self.settings.window_size
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg='#f0f0f0')
        
        # ウィンドウのリサイズ設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="画像リサイズ & 圧縮アプリ", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 左側：操作パネル
        self.setup_control_panel(main_frame)
        
        # 右側：プレビュー
        self.setup_preview_panel(main_frame)
        
        # 下部：進捗バーとボタン
        self.setup_bottom_panel(main_frame)
    
    def setup_control_panel(self, parent):
        """左側の操作パネルを設定"""
        control_frame = ttk.LabelFrame(parent, text="設定", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # ファイル選択ボタン
        ttk.Button(control_frame, text="ファイルを選択", 
                  command=self._select_file).grid(row=0, column=0, columnspan=2, 
                                               sticky=(tk.W, tk.E), pady=(0, 10))
        
        # リサイズ設定
        self.setup_resize_controls(control_frame)
        
        # 圧縮設定
        self.setup_compression_controls(control_frame)
        
        # プレビューボタン
        ttk.Button(control_frame, text="プレビュー更新", 
                  command=self._update_preview).grid(row=3, column=0, columnspan=2, 
                                                   sticky=(tk.W, tk.E), pady=5)
    
    def setup_resize_controls(self, parent):
        """リサイズ設定UIを設定"""
        resize_frame = ttk.LabelFrame(parent, text="リサイズ設定", padding="5")
        resize_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 幅
        ttk.Label(resize_frame, text="幅:").grid(row=0, column=0, sticky=tk.W)
        self.width_var = tk.StringVar(value=str(self.settings.resize_settings.width))
        self.width_entry = ttk.Entry(resize_frame, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=0, column=1, padx=5)
        self.width_entry.bind('<KeyRelease>', self._on_width_change)
        
        # 高さ
        ttk.Label(resize_frame, text="高さ:").grid(row=1, column=0, sticky=tk.W)
        self.height_var = tk.StringVar(value=str(self.settings.resize_settings.height))
        self.height_entry = ttk.Entry(resize_frame, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=1, column=1, padx=5)
        
        # 比率維持チェック
        self.maintain_ratio_var = tk.BooleanVar(value=self.settings.resize_settings.maintain_ratio)
        ttk.Checkbutton(resize_frame, text="比率を維持", 
                       variable=self.maintain_ratio_var,
                       command=self._on_ratio_change).grid(row=2, column=0, columnspan=2, 
                                                         sticky=tk.W, pady=5)
        
        # リサイズ方法
        ttk.Label(resize_frame, text="リサイズ方法:").grid(row=3, column=0, sticky=tk.W)
        self.resize_method_var = tk.StringVar(value=self.settings.resize_settings.method)
        method_combo = ttk.Combobox(resize_frame, textvariable=self.resize_method_var,
                                   values=["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],
                                   state="readonly", width=12)
        method_combo.grid(row=3, column=1, padx=5)
    
    def setup_compression_controls(self, parent):
        """圧縮設定UIを設定"""
        compress_frame = ttk.LabelFrame(parent, text="圧縮設定", padding="5")
        compress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 出力形式
        ttk.Label(compress_frame, text="出力形式:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value=self.settings.compression_settings.format_type)
        format_combo = ttk.Combobox(compress_frame, textvariable=self.format_var,
                                   values=self.settings.get_supported_output_formats(),
                                   state="readonly", width=12)
        format_combo.grid(row=0, column=1, padx=5)
        format_combo.bind("<<ComboboxSelected>>", self._on_format_change)
        
        # 品質設定
        ttk.Label(compress_frame, text="品質:").grid(row=1, column=0, sticky=tk.W)
        self.quality_var = tk.IntVar(value=self.settings.compression_settings.quality)
        self.quality_scale = ttk.Scale(compress_frame, from_=10, to=100, 
                                      variable=self.quality_var, orient=tk.HORIZONTAL)
        self.quality_scale.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.quality_label = ttk.Label(compress_frame, text=f"{self.quality_var.get()}%")
        self.quality_label.grid(row=1, column=2, padx=5)
        self.quality_scale.configure(command=self._update_quality_label)
    
    def setup_preview_panel(self, parent):
        """右側のプレビューパネルを設定"""
        preview_frame = ttk.LabelFrame(parent, text="プレビュー", padding="10")
        preview_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # ドラッグ&ドロップエリア
        self.drop_area = tk.Label(preview_frame, 
                                 text="ここに画像ファイルをドラッグ&ドロップ\nまたは「ファイルを選択」ボタンをクリック",
                                 bg='white', 
                                 relief='solid',
                                 bd=2,
                                 font=('Arial', 12))
        self.drop_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                           padx=10, pady=10)
    
    def setup_bottom_panel(self, parent):
        """下部のパネルを設定"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(1, weight=1)
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, 
                                           mode='determinate')
        self.progress_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ボタン
        ttk.Button(bottom_frame, text="保存", 
                  command=self._save).grid(row=1, column=0, padx=(0, 5))
        
        ttk.Button(bottom_frame, text="名前を付けて保存", 
                  command=self._save_as).grid(row=1, column=1, padx=5)
        
        ttk.Button(bottom_frame, text="リセット", 
                  command=self._reset).grid(row=1, column=2, padx=(5, 0))
    
    def setup_drag_drop(self):
        """ドラッグ&ドロップを設定"""
        self.drop_area.drop_target_register(tkdnd.DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self._on_drop_event)
    
    def _select_file(self):
        """ファイル選択ダイアログ"""
        file_path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[
                ("画像ファイル", " ".join(self.settings.get_supported_input_formats())),
                ("すべてのファイル", "*.*")
            ]
        )
        if file_path and self.on_file_select:
            self.on_file_select(file_path)
    
    def _on_drop_event(self, event):
        """ドラッグ&ドロップ時の処理"""
        if self.on_drop:
            self.on_drop(event.data)
    
    def _update_preview(self):
        """プレビュー更新"""
        if self.on_preview_update:
            self.on_preview_update()
    
    def _save(self):
        """保存"""
        if self.on_save:
            self.on_save()
    
    def _save_as(self):
        """名前を付けて保存"""
        if self.on_save_as:
            self.on_save_as()
    
    def _reset(self):
        """リセット"""
        if self.on_reset:
            self.on_reset()
    
    def _on_width_change(self, event=None):
        """幅変更時の処理"""
        if self.maintain_ratio_var.get() and self.on_settings_change:
            self.on_settings_change()
    
    def _on_ratio_change(self):
        """比率維持チェック変更時の処理"""
        if self.on_settings_change:
            self.on_settings_change()
    
    def _on_format_change(self, event=None):
        """出力形式変更時の処理"""
        format_type = self.format_var.get()
        # PNGの場合は品質設定を無効化
        if format_type == "PNG":
            self.quality_scale.configure(state='disabled')
            self.quality_label.configure(text="N/A")
        else:
            self.quality_scale.configure(state='normal')
            self._update_quality_label()
    
    def _update_quality_label(self, value=None):
        """品質ラベルを更新"""
        if self.format_var.get() != "PNG":
            self.quality_label.configure(text=f"{int(self.quality_var.get())}%")
    
    def update_preview_image(self, pil_image):
        """プレビュー画像を更新"""
        self.preview_image = ImageTk.PhotoImage(pil_image)
        self.drop_area.configure(image=self.preview_image, text="")
    
    def clear_preview(self):
        """プレビューをクリア"""
        self.drop_area.configure(image="", 
                               text="ここに画像ファイルをドラッグ&ドロップ\nまたは「ファイルを選択」ボタンをクリック")
        self.preview_image = None
    
    def update_size_fields(self, width: int, height: int):
        """サイズフィールドを更新"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
    
    def get_resize_settings_from_ui(self):
        """UIからリサイズ設定を取得"""
        try:
            self.settings.resize_settings.width = int(self.width_var.get())
            self.settings.resize_settings.height = int(self.height_var.get())
            self.settings.resize_settings.maintain_ratio = self.maintain_ratio_var.get()
            self.settings.resize_settings.method = self.resize_method_var.get()
        except ValueError:
            raise ValueError("無効なサイズが指定されました")
    
    def get_compression_settings_from_ui(self):
        """UIから圧縮設定を取得"""
        self.settings.compression_settings.format_type = self.format_var.get()
        self.settings.compression_settings.quality = int(self.quality_var.get())
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """メッセージを表示"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
    
    def start_progress(self):
        """進捗バーを開始"""
        self.progress_var.set(0)
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
    
    def stop_progress(self, final_value: int = 100):
        """進捗バーを停止"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.progress_var.set(final_value) 