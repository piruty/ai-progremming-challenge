"""
アプリケーション設定管理モデル
"""

from dataclasses import dataclass
from typing import Tuple
from PIL import Image


@dataclass
class ResizeSettings:
    """リサイズ設定を管理するデータクラス"""
    width: int = 800
    height: int = 600
    maintain_ratio: bool = True
    method: str = "LANCZOS"
    
    def get_pil_resample_method(self) -> int:
        """PIL用のリサンプリングメソッドを取得"""
        method_map = {
            "LANCZOS": Image.LANCZOS,
            "BICUBIC": Image.BICUBIC,
            "BILINEAR": Image.BILINEAR,
            "NEAREST": Image.NEAREST
        }
        return method_map.get(self.method, Image.LANCZOS)


@dataclass
class CompressionSettings:
    """圧縮設定を管理するデータクラス"""
    format_type: str = "JPEG"
    quality: int = 85
    
    def get_file_extension(self) -> str:
        """ファイル拡張子を取得"""
        format_ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
        return format_ext.get(self.format_type, ".jpg")
    
    def get_save_kwargs(self) -> dict:
        """保存時のキーワード引数を取得"""
        kwargs = {}
        
        if self.format_type in ["JPEG", "WEBP"]:
            kwargs['quality'] = self.quality
            kwargs['optimize'] = True
        elif self.format_type == "PNG":
            kwargs['optimize'] = True
            
        return kwargs


@dataclass
class AppSettings:
    """アプリケーション全体の設定を管理するデータクラス"""
    window_size: Tuple[int, int] = (800, 600)
    preview_size: Tuple[int, int] = (400, 300)
    
    # デフォルト設定
    resize_settings: ResizeSettings = None
    compression_settings: CompressionSettings = None
    
    def __post_init__(self):
        """初期化後に実行される処理"""
        if self.resize_settings is None:
            self.resize_settings = ResizeSettings()
        if self.compression_settings is None:
            self.compression_settings = CompressionSettings()
    
    @classmethod
    def get_supported_input_formats(cls) -> list:
        """対応している入力ファイル形式を取得"""
        return ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff", "*.webp"]
    
    @classmethod
    def get_supported_output_formats(cls) -> list:
        """対応している出力ファイル形式を取得"""
        return ["JPEG", "PNG", "WEBP"] 