"""
設定モデルのユニットテスト
"""

import unittest
from PIL import Image

from models.settings import ResizeSettings, CompressionSettings, AppSettings


class TestResizeSettings(unittest.TestCase):
    """ResizeSettingsクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        settings = ResizeSettings()
        self.assertEqual(settings.width, 800)
        self.assertEqual(settings.height, 600)
        self.assertTrue(settings.maintain_ratio)
        self.assertEqual(settings.method, "LANCZOS")
    
    def test_custom_values(self):
        """カスタム値のテスト"""
        settings = ResizeSettings(width=1200, height=800, maintain_ratio=False, method="BICUBIC")
        self.assertEqual(settings.width, 1200)
        self.assertEqual(settings.height, 800)
        self.assertFalse(settings.maintain_ratio)
        self.assertEqual(settings.method, "BICUBIC")
    
    def test_get_pil_resample_method(self):
        """PILリサンプリングメソッド変換のテスト"""
        settings = ResizeSettings()
        
        settings.method = "LANCZOS"
        self.assertEqual(settings.get_pil_resample_method(), Image.LANCZOS)
        
        settings.method = "BICUBIC"
        self.assertEqual(settings.get_pil_resample_method(), Image.BICUBIC)
        
        settings.method = "BILINEAR"
        self.assertEqual(settings.get_pil_resample_method(), Image.BILINEAR)
        
        settings.method = "NEAREST"
        self.assertEqual(settings.get_pil_resample_method(), Image.NEAREST)
        
        # 無効な値の場合はデフォルト（LANCZOS）を返す
        settings.method = "INVALID"
        self.assertEqual(settings.get_pil_resample_method(), Image.LANCZOS)


class TestCompressionSettings(unittest.TestCase):
    """CompressionSettingsクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        settings = CompressionSettings()
        self.assertEqual(settings.format_type, "JPEG")
        self.assertEqual(settings.quality, 85)
    
    def test_custom_values(self):
        """カスタム値のテスト"""
        settings = CompressionSettings(format_type="PNG", quality=90)
        self.assertEqual(settings.format_type, "PNG")
        self.assertEqual(settings.quality, 90)
    
    def test_get_file_extension(self):
        """ファイル拡張子取得のテスト"""
        settings = CompressionSettings()
        
        settings.format_type = "JPEG"
        self.assertEqual(settings.get_file_extension(), ".jpg")
        
        settings.format_type = "PNG"
        self.assertEqual(settings.get_file_extension(), ".png")
        
        settings.format_type = "WEBP"
        self.assertEqual(settings.get_file_extension(), ".webp")
        
        # 無効な値の場合はデフォルト（.jpg）を返す
        settings.format_type = "INVALID"
        self.assertEqual(settings.get_file_extension(), ".jpg")
    
    def test_get_save_kwargs_jpeg(self):
        """JPEG保存キーワード引数のテスト"""
        settings = CompressionSettings(format_type="JPEG", quality=75)
        kwargs = settings.get_save_kwargs()
        
        expected = {'quality': 75, 'optimize': True}
        self.assertEqual(kwargs, expected)
    
    def test_get_save_kwargs_webp(self):
        """WEBP保存キーワード引数のテスト"""
        settings = CompressionSettings(format_type="WEBP", quality=80)
        kwargs = settings.get_save_kwargs()
        
        expected = {'quality': 80, 'optimize': True}
        self.assertEqual(kwargs, expected)
    
    def test_get_save_kwargs_png(self):
        """PNG保存キーワード引数のテスト"""
        settings = CompressionSettings(format_type="PNG")
        kwargs = settings.get_save_kwargs()
        
        expected = {'optimize': True}
        self.assertEqual(kwargs, expected)


class TestAppSettings(unittest.TestCase):
    """AppSettingsクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値のテスト"""
        settings = AppSettings()
        self.assertEqual(settings.window_size, (800, 600))
        self.assertEqual(settings.preview_size, (400, 300))
        self.assertIsInstance(settings.resize_settings, ResizeSettings)
        self.assertIsInstance(settings.compression_settings, CompressionSettings)
    
    def test_custom_values(self):
        """カスタム値のテスト"""
        resize_settings = ResizeSettings(width=1000, height=800)
        compression_settings = CompressionSettings(format_type="PNG")
        
        settings = AppSettings(
            window_size=(1024, 768),
            preview_size=(500, 400),
            resize_settings=resize_settings,
            compression_settings=compression_settings
        )
        
        self.assertEqual(settings.window_size, (1024, 768))
        self.assertEqual(settings.preview_size, (500, 400))
        self.assertEqual(settings.resize_settings.width, 1000)
        self.assertEqual(settings.compression_settings.format_type, "PNG")
    
    def test_post_init(self):
        """初期化後処理のテスト"""
        # resize_settingsがNoneの場合に自動初期化される
        settings = AppSettings(resize_settings=None)
        self.assertIsInstance(settings.resize_settings, ResizeSettings)
        
        # compression_settingsがNoneの場合に自動初期化される
        settings = AppSettings(compression_settings=None)
        self.assertIsInstance(settings.compression_settings, CompressionSettings)
    
    def test_get_supported_input_formats(self):
        """対応入力形式取得のテスト"""
        formats = AppSettings.get_supported_input_formats()
        expected = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff", "*.webp"]
        self.assertEqual(formats, expected)
    
    def test_get_supported_output_formats(self):
        """対応出力形式取得のテスト"""
        formats = AppSettings.get_supported_output_formats()
        expected = ["JPEG", "PNG", "WEBP"]
        self.assertEqual(formats, expected)


if __name__ == '__main__':
    unittest.main() 