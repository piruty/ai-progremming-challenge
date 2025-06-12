"""
画像処理モデル
"""

from typing import Tuple, Optional
from PIL import Image
from pathlib import Path

from .settings import ResizeSettings, CompressionSettings


class ImageProcessor:
    """画像処理を行うクラス"""
    
    def __init__(self):
        self.original_image: Optional[Image.Image] = None
        self.current_image: Optional[Image.Image] = None
        self.image_path: Optional[str] = None
    
    def load_image(self, file_path: str) -> bool:
        """画像を読み込み"""
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.current_image = self.original_image.copy()
            return True
        except Exception as e:
            raise ValueError(f"画像の読み込みに失敗しました: {str(e)}")
    
    def get_original_size(self) -> Optional[Tuple[int, int]]:
        """元の画像サイズを取得"""
        if self.original_image:
            return self.original_image.size
        return None
    
    def get_current_size(self) -> Optional[Tuple[int, int]]:
        """現在の画像サイズを取得"""
        if self.current_image:
            return self.current_image.size
        return None
    
    def calculate_size_with_ratio(self, target_width: int, target_height: int, 
                                maintain_ratio: bool) -> Tuple[int, int]:
        """比率を考慮したサイズを計算"""
        if not self.original_image:
            return target_width, target_height
        
        if not maintain_ratio:
            return target_width, target_height
        
        original_width, original_height = self.original_image.size
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        return new_width, new_height
    
    def resize_image(self, resize_settings: ResizeSettings) -> Image.Image:
        """画像をリサイズ"""
        if not self.original_image:
            raise ValueError("リサイズする画像がありません")
        
        # サイズ計算
        new_width, new_height = self.calculate_size_with_ratio(
            resize_settings.width,
            resize_settings.height,
            resize_settings.maintain_ratio
        )
        
        # リサイズ実行
        resample_method = resize_settings.get_pil_resample_method()
        resized_image = self.original_image.resize(
            (new_width, new_height), 
            resample_method
        )
        
        self.current_image = resized_image
        return resized_image
    
    def create_preview(self, preview_size: Tuple[int, int]) -> Optional[Image.Image]:
        """プレビュー用の画像を作成"""
        if not self.current_image:
            return None
        
        preview_image = self.current_image.copy()
        preview_image.thumbnail(preview_size, Image.LANCZOS)
        return preview_image
    
    def save_image(self, file_path: str, compression_settings: CompressionSettings):
        """画像を保存"""
        if not self.current_image:
            raise ValueError("保存する画像がありません")
        
        save_kwargs = compression_settings.get_save_kwargs()
        self.current_image.save(
            file_path, 
            format=compression_settings.format_type, 
            **save_kwargs
        )
    
    def generate_output_filename(self, compression_settings: CompressionSettings, 
                                suffix: str = "_resized") -> str:
        """出力ファイル名を生成"""
        if not self.image_path:
            raise ValueError("元の画像パスがありません")
        
        path = Path(self.image_path)
        ext = compression_settings.get_file_extension()
        return str(path.parent / f"{path.stem}{suffix}{ext}")
    
    def reset_to_original(self):
        """元の画像に戻す"""
        if self.original_image:
            self.current_image = self.original_image.copy()
    
    def clear_images(self):
        """画像をクリア"""
        self.original_image = None
        self.current_image = None
        self.image_path = None
    
    def has_image(self) -> bool:
        """画像が読み込まれているかチェック"""
        return self.original_image is not None 