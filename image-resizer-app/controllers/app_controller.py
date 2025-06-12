"""
アプリケーションコントローラー
"""

import threading
from tkinter import filedialog
from typing import Optional

from models.settings import AppSettings
from models.image_processor import ImageProcessor
from views.main_window import MainWindow
from utils.file_utils import extract_file_path_from_drop_data, validate_output_path


class AppController:
    """アプリケーションのメインコントローラー"""
    
    def __init__(self, window: MainWindow, settings: AppSettings):
        self.window = window
        self.settings = settings
        self.image_processor = ImageProcessor()
        
        # ビューのコールバックを設定
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """ビューのコールバック関数を設定"""
        self.window.on_file_select = self.handle_file_select
        self.window.on_drop = self.handle_drop
        self.window.on_preview_update = self.handle_preview_update
        self.window.on_save = self.handle_save
        self.window.on_save_as = self.handle_save_as
        self.window.on_reset = self.handle_reset
        self.window.on_settings_change = self.handle_settings_change
    
    def handle_file_select(self, file_path: str):
        """ファイル選択時の処理"""
        self.load_image(file_path)
    
    def handle_drop(self, drop_data: str):
        """ドラッグ&ドロップ時の処理"""
        file_path = extract_file_path_from_drop_data(drop_data)
        if file_path:
            self.load_image(file_path)
        else:
            self.window.show_message("エラー", "対応していないファイル形式です", "error")
    
    def load_image(self, file_path: str):
        """画像を読み込み"""
        try:
            self.image_processor.load_image(file_path)
            original_size = self.image_processor.get_original_size()
            
            if original_size:
                width, height = original_size
                # UIの設定を更新
                self.window.update_size_fields(width, height)
                # 設定オブジェクトも更新
                self.settings.resize_settings.width = width
                self.settings.resize_settings.height = height
                
                # プレビューを更新
                self.update_preview()
                
                self.window.show_message(
                    "成功", 
                    f"画像を読み込みました\nサイズ: {width} x {height}",
                    "info"
                )
                
        except Exception as e:
            self.window.show_message("エラー", str(e), "error")
    
    def handle_preview_update(self):
        """プレビュー更新時の処理"""
        self.update_preview()
    
    def update_preview(self):
        """プレビューを更新"""
        if not self.image_processor.has_image():
            return
        
        try:
            # UIから設定を取得
            self.window.get_resize_settings_from_ui()
            
            # 画像をリサイズ
            resized_image = self.image_processor.resize_image(self.settings.resize_settings)
            
            # プレビュー用画像を作成
            preview_image = self.image_processor.create_preview(self.settings.preview_size)
            if preview_image:
                self.window.update_preview_image(preview_image)
            
            # 新しいサイズをUIに反映
            new_size = self.image_processor.get_current_size()
            if new_size:
                self.window.update_size_fields(new_size[0], new_size[1])
                
        except ValueError as e:
            self.window.show_message("エラー", str(e), "error")
        except Exception as e:
            self.window.show_message("エラー", f"プレビューの更新に失敗しました: {str(e)}", "error")
    
    def handle_settings_change(self):
        """設定変更時の処理（比率維持など）"""
        if not self.image_processor.has_image():
            return
        
        try:
            self.window.get_resize_settings_from_ui()
            
            if self.settings.resize_settings.maintain_ratio:
                # 幅を基準に高さを自動調整
                original_size = self.image_processor.get_original_size()
                if original_size:
                    original_width, original_height = original_size
                    target_width = self.settings.resize_settings.width
                    
                    ratio = target_width / original_width
                    new_height = int(original_height * ratio)
                    
                    self.settings.resize_settings.height = new_height
                    self.window.update_size_fields(target_width, new_height)
                    
        except ValueError:
            pass  # 無効な値の場合は無視
    
    def handle_save(self):
        """保存時の処理"""
        if not self.image_processor.has_image():
            self.window.show_message("警告", "保存する画像がありません", "warning")
            return
        
        try:
            # UIから設定を取得
            self.window.get_compression_settings_from_ui()
            
            # 出力ファイル名を生成
            output_path = self.image_processor.generate_output_filename(
                self.settings.compression_settings
            )
            
            # 保存処理を実行
            self._save_image_async(output_path)
            
        except Exception as e:
            self.window.show_message("エラー", f"保存に失敗しました: {str(e)}", "error")
    
    def handle_save_as(self):
        """名前を付けて保存時の処理"""
        if not self.image_processor.has_image():
            self.window.show_message("警告", "保存する画像がありません", "warning")
            return
        
        # UIから設定を取得
        self.window.get_compression_settings_from_ui()
        
        # ファイル保存ダイアログ
        ext = self.settings.compression_settings.get_file_extension()
        file_path = filedialog.asksaveasfilename(
            title="名前を付けて保存",
            defaultextension=ext,
            filetypes=[
                (f"{self.settings.compression_settings.format_type}ファイル", f"*{ext}"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            self._save_image_async(file_path)
    
    def _save_image_async(self, file_path: str):
        """画像を非同期で保存"""
        def save_thread():
            try:
                # 進捗バー開始
                self.window.root.after(0, self.window.start_progress)
                
                # 保存処理
                self.image_processor.save_image(file_path, self.settings.compression_settings)
                
                # 成功メッセージ
                self.window.root.after(0, lambda: self._on_save_success(file_path))
                
            except Exception as e:
                # エラーメッセージ
                self.window.root.after(0, lambda: self._on_save_error(str(e)))
        
        # バックグラウンドで保存処理を実行
        threading.Thread(target=save_thread, daemon=True).start()
    
    def _on_save_success(self, file_path: str):
        """保存成功時の処理"""
        self.window.stop_progress(100)
        self.window.show_message("成功", f"画像を保存しました:\n{file_path}", "info")
    
    def _on_save_error(self, error_message: str):
        """保存エラー時の処理"""
        self.window.stop_progress(0)
        self.window.show_message("エラー", f"保存に失敗しました:\n{error_message}", "error")
    
    def handle_reset(self):
        """リセット時の処理"""
        if self.image_processor.has_image():
            # 元の画像に戻す
            self.image_processor.reset_to_original()
            original_size = self.image_processor.get_original_size()
            
            if original_size:
                width, height = original_size
                self.window.update_size_fields(width, height)
                self.settings.resize_settings.width = width
                self.settings.resize_settings.height = height
                
                # プレビューを更新
                self.update_preview()
        else:
            # 画像がない場合はプレビューをクリア
            self.window.clear_preview()
            self.image_processor.clear_images()
    
    def shutdown(self):
        """アプリケーション終了時の処理"""
        # 必要に応じて設定の保存やリソースのクリーンアップを行う
        pass 