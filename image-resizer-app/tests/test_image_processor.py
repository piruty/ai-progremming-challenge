"""
画像処理モデルのユニットテスト
"""

import unittest
import tempfile
import os
from PIL import Image
from pathlib import Path

from models.image_processor import ImageProcessor
from models.settings import ResizeSettings, CompressionSettings


class TestImageProcessor(unittest.TestCase):
    """ImageProcessorクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.processor = ImageProcessor()
        
        # テスト用の一時画像を作成
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        
        # 100x100のテスト画像を作成
        test_image = Image.new('RGB', (100, 100), color='red')
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ファイルを削除
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        os.rmdir(self.temp_dir)
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertIsNone(self.processor.original_image)
        self.assertIsNone(self.processor.current_image)
        self.assertIsNone(self.processor.image_path)
        self.assertFalse(self.processor.has_image())
    
    def test_load_image_success(self):
        """画像読み込み成功のテスト"""
        result = self.processor.load_image(self.test_image_path)
        
        self.assertTrue(result)
        self.assertIsNotNone(self.processor.original_image)
        self.assertIsNotNone(self.processor.current_image)
        self.assertEqual(self.processor.image_path, self.test_image_path)
        self.assertTrue(self.processor.has_image())
        
        # サイズが正しいかチェック
        self.assertEqual(self.processor.get_original_size(), (100, 100))
        self.assertEqual(self.processor.get_current_size(), (100, 100))
    
    def test_load_image_failure(self):
        """画像読み込み失敗のテスト"""
        with self.assertRaises(ValueError):
            self.processor.load_image("non_existent_file.jpg")
    
    def test_calculate_size_with_ratio_maintain(self):
        """比率維持でのサイズ計算テスト"""
        self.processor.load_image(self.test_image_path)
        
        # 比率維持ありの場合
        new_width, new_height = self.processor.calculate_size_with_ratio(200, 300, True)
        self.assertEqual(new_width, 200)
        self.assertEqual(new_height, 200)  # 正方形なので同じサイズ
    
    def test_calculate_size_without_ratio_maintain(self):
        """比率維持なしでのサイズ計算テスト"""
        self.processor.load_image(self.test_image_path)
        
        # 比率維持なしの場合
        new_width, new_height = self.processor.calculate_size_with_ratio(200, 300, False)
        self.assertEqual(new_width, 200)
        self.assertEqual(new_height, 300)
    
    def test_resize_image(self):
        """画像リサイズのテスト"""
        self.processor.load_image(self.test_image_path)
        
        resize_settings = ResizeSettings(width=50, height=50, maintain_ratio=False)
        resized_image = self.processor.resize_image(resize_settings)
        
        self.assertEqual(resized_image.size, (50, 50))
        self.assertEqual(self.processor.get_current_size(), (50, 50))
    
    def test_resize_image_without_loaded_image(self):
        """画像未読み込み時のリサイズエラーテスト"""
        resize_settings = ResizeSettings()
        
        with self.assertRaises(ValueError):
            self.processor.resize_image(resize_settings)
    
    def test_create_preview(self):
        """プレビュー作成のテスト"""
        self.processor.load_image(self.test_image_path)
        
        preview_image = self.processor.create_preview((50, 50))
        self.assertIsNotNone(preview_image)
        # サムネイルなので元のサイズ以下になる
        self.assertLessEqual(preview_image.size[0], 50)
        self.assertLessEqual(preview_image.size[1], 50)
    
    def test_create_preview_without_image(self):
        """画像未読み込み時のプレビュー作成テスト"""
        preview_image = self.processor.create_preview((50, 50))
        self.assertIsNone(preview_image)
    
    def test_generate_output_filename(self):
        """出力ファイル名生成のテスト"""
        self.processor.load_image(self.test_image_path)
        
        compression_settings = CompressionSettings(format_type="JPEG")
        output_filename = self.processor.generate_output_filename(compression_settings)
        
        expected_filename = os.path.join(self.temp_dir, "test_image_resized.jpg")
        self.assertEqual(output_filename, expected_filename)
    
    def test_generate_output_filename_without_image(self):
        """画像未読み込み時の出力ファイル名生成エラーテスト"""
        compression_settings = CompressionSettings()
        
        with self.assertRaises(ValueError):
            self.processor.generate_output_filename(compression_settings)
    
    def test_save_image(self):
        """画像保存のテスト"""
        self.processor.load_image(self.test_image_path)
        
        # リサイズしてから保存
        resize_settings = ResizeSettings(width=50, height=50)
        self.processor.resize_image(resize_settings)
        
        # 保存
        output_path = os.path.join(self.temp_dir, "output.jpg")
        compression_settings = CompressionSettings(format_type="JPEG", quality=90)
        
        self.processor.save_image(output_path, compression_settings)
        
        # ファイルが作成されたかチェック
        self.assertTrue(os.path.exists(output_path))
        
        # 保存された画像を読み込んでサイズを確認
        saved_image = Image.open(output_path)
        self.assertEqual(saved_image.size, (50, 50))
        
        # クリーンアップ
        os.remove(output_path)
    
    def test_save_image_without_current_image(self):
        """現在画像未設定時の保存エラーテスト"""
        compression_settings = CompressionSettings()
        
        with self.assertRaises(ValueError):
            self.processor.save_image("output.jpg", compression_settings)
    
    def test_reset_to_original(self):
        """元画像へのリセットテスト"""
        self.processor.load_image(self.test_image_path)
        
        # リサイズして現在画像を変更
        resize_settings = ResizeSettings(width=50, height=50)
        self.processor.resize_image(resize_settings)
        self.assertEqual(self.processor.get_current_size(), (50, 50))
        
        # 元に戻す
        self.processor.reset_to_original()
        self.assertEqual(self.processor.get_current_size(), (100, 100))
    
    def test_clear_images(self):
        """画像クリアのテスト"""
        self.processor.load_image(self.test_image_path)
        self.assertTrue(self.processor.has_image())
        
        self.processor.clear_images()
        
        self.assertIsNone(self.processor.original_image)
        self.assertIsNone(self.processor.current_image)
        self.assertIsNone(self.processor.image_path)
        self.assertFalse(self.processor.has_image())


if __name__ == '__main__':
    unittest.main() 