"""
ファイルユーティリティのユニットテスト
"""

import unittest
import tempfile
import os
from pathlib import Path

from utils.file_utils import (
    is_supported_image_file,
    extract_file_path_from_drop_data,
    get_file_size_mb,
    ensure_unique_filename,
    create_backup_filename,
    get_directory_images,
    validate_output_path
)


class TestFileUtils(unittest.TestCase):
    """ファイルユーティリティのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ディレクトリとファイルを削除
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_is_supported_image_file(self):
        """対応画像ファイル判定のテスト"""
        # 対応している拡張子
        self.assertTrue(is_supported_image_file("test.jpg"))
        self.assertTrue(is_supported_image_file("test.jpeg"))
        self.assertTrue(is_supported_image_file("test.png"))
        self.assertTrue(is_supported_image_file("test.bmp"))
        self.assertTrue(is_supported_image_file("test.gif"))
        self.assertTrue(is_supported_image_file("test.tiff"))
        self.assertTrue(is_supported_image_file("test.webp"))
        
        # 大文字小文字混在
        self.assertTrue(is_supported_image_file("test.JPG"))
        self.assertTrue(is_supported_image_file("test.Png"))
        
        # 対応していない拡張子
        self.assertFalse(is_supported_image_file("test.txt"))
        self.assertFalse(is_supported_image_file("test.pdf"))
        self.assertFalse(is_supported_image_file("test.doc"))
        
        # 拡張子なし
        self.assertFalse(is_supported_image_file("test"))
    
    def test_extract_file_path_from_drop_data(self):
        """ドロップデータからファイルパス抽出のテスト"""
        # テスト用画像ファイルを作成
        test_file = os.path.join(self.temp_dir, "test.jpg")
        Path(test_file).touch()
        
        # 正常なケース
        drop_data = f"{test_file}"
        result = extract_file_path_from_drop_data(drop_data)
        self.assertEqual(result, test_file)
        
        # 括弧付きのケース
        drop_data = f"{{{test_file}}}"
        result = extract_file_path_from_drop_data(drop_data)
        self.assertEqual(result, test_file)
        
        # 存在しないファイル
        drop_data = "/non/existent/file.jpg"
        result = extract_file_path_from_drop_data(drop_data)
        self.assertIsNone(result)
        
        # 対応していない拡張子
        test_txt_file = os.path.join(self.temp_dir, "test.txt")
        Path(test_txt_file).touch()
        drop_data = test_txt_file
        result = extract_file_path_from_drop_data(drop_data)
        self.assertIsNone(result)
        
        # 空のデータ
        result = extract_file_path_from_drop_data("")
        self.assertIsNone(result)
        
        # クリーンアップ
        os.remove(test_file)
        os.remove(test_txt_file)
    
    def test_get_file_size_mb(self):
        """ファイルサイズ（MB）取得のテスト"""
        # テストファイル作成（約1KB）
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("x" * 1024)  # 1KB
        
        size_mb = get_file_size_mb(test_file)
        self.assertAlmostEqual(size_mb, 1024 / (1024 * 1024), places=6)
        
        # 存在しないファイル
        size_mb = get_file_size_mb("/non/existent/file.txt")
        self.assertEqual(size_mb, 0.0)
        
        # クリーンアップ
        os.remove(test_file)
    
    def test_ensure_unique_filename(self):
        """一意ファイル名生成のテスト"""
        # 存在しないファイルの場合、そのまま返される
        non_existent = os.path.join(self.temp_dir, "non_existent.txt")
        result = ensure_unique_filename(non_existent)
        self.assertEqual(result, non_existent)
        
        # 既存ファイルがある場合
        existing_file = os.path.join(self.temp_dir, "existing.txt")
        Path(existing_file).touch()
        
        unique_name = ensure_unique_filename(existing_file)
        expected = os.path.join(self.temp_dir, "existing_1.txt")
        self.assertEqual(unique_name, expected)
        
        # さらに_1も存在する場合
        Path(expected).touch()
        unique_name = ensure_unique_filename(existing_file)
        expected_2 = os.path.join(self.temp_dir, "existing_2.txt")
        self.assertEqual(unique_name, expected_2)
        
        # クリーンアップ
        os.remove(existing_file)
        os.remove(expected)
    
    def test_create_backup_filename(self):
        """バックアップファイル名生成のテスト"""
        original_file = os.path.join(self.temp_dir, "original.jpg")
        backup_name = create_backup_filename(original_file)
        expected = os.path.join(self.temp_dir, "original_backup.jpg")
        self.assertEqual(backup_name, expected)
        
        # 拡張子なしの場合
        original_file = os.path.join(self.temp_dir, "original")
        backup_name = create_backup_filename(original_file)
        expected = os.path.join(self.temp_dir, "original_backup")
        self.assertEqual(backup_name, expected)
    
    def test_get_directory_images(self):
        """ディレクトリ内画像ファイル取得のテスト"""
        # テスト用ファイルを作成
        image_files = ["image1.jpg", "image2.png", "image3.gif"]
        non_image_files = ["text.txt", "document.pdf"]
        
        for filename in image_files + non_image_files:
            Path(os.path.join(self.temp_dir, filename)).touch()
        
        # 画像ファイルのみを取得
        result = get_directory_images(self.temp_dir)
        
        expected_paths = [os.path.join(self.temp_dir, f) for f in image_files]
        expected_paths.sort()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result, expected_paths)
        
        # 存在しないディレクトリ
        result = get_directory_images("/non/existent/directory")
        self.assertEqual(result, [])
        
        # クリーンアップ
        for filename in image_files + non_image_files:
            os.remove(os.path.join(self.temp_dir, filename))
    
    def test_validate_output_path(self):
        """出力パス検証のテスト"""
        # 有効なパス（存在するディレクトリ内）
        valid_path = os.path.join(self.temp_dir, "output.jpg")
        self.assertTrue(validate_output_path(valid_path))
        
        # 無効なパス（存在しないディレクトリ）
        invalid_path = "/non/existent/directory/output.jpg"
        self.assertFalse(validate_output_path(invalid_path))
        
        # 無効なパス形式
        self.assertFalse(validate_output_path(""))


if __name__ == '__main__':
    unittest.main() 