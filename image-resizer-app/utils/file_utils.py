"""
ファイル操作ユーティリティ
"""

import os
from pathlib import Path
from typing import List, Optional


def is_supported_image_file(file_path: str) -> bool:
    """対応している画像ファイルかチェック"""
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    file_ext = Path(file_path).suffix.lower()
    return file_ext in supported_extensions


def extract_file_path_from_drop_data(drop_data: str) -> Optional[str]:
    """ドラッグ&ドロップのデータからファイルパスを抽出"""
    files = drop_data.split()
    if files:
        # 括弧やクォートを除去
        file_path = files[0].strip('{}').strip('"').strip("'")
        if os.path.exists(file_path) and is_supported_image_file(file_path):
            return file_path
    return None


def get_file_size_mb(file_path: str) -> float:
    """ファイルサイズをMB単位で取得"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def ensure_unique_filename(file_path: str) -> str:
    """重複しないファイル名を生成"""
    path = Path(file_path)
    if not path.exists():
        return file_path
    
    base_name = path.stem
    extension = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_name = f"{base_name}_{counter}{extension}"
        new_path = parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


def create_backup_filename(file_path: str) -> str:
    """バックアップファイル名を生成"""
    path = Path(file_path)
    backup_name = f"{path.stem}_backup{path.suffix}"
    return str(path.parent / backup_name)


def get_directory_images(directory: str) -> List[str]:
    """ディレクトリ内の画像ファイル一覧を取得"""
    images = []
    try:
        dir_path = Path(directory)
        if dir_path.is_dir():
            for file_path in dir_path.iterdir():
                if file_path.is_file() and is_supported_image_file(str(file_path)):
                    images.append(str(file_path))
    except (OSError, PermissionError):
        pass
    
    return sorted(images)


def validate_output_path(file_path: str) -> bool:
    """出力パスが有効かチェック"""
    # 空文字列の場合は無効
    if not file_path.strip():
        return False
        
    try:
        path = Path(file_path)
        # 親ディレクトリが存在し、書き込み可能かチェック
        parent_dir = path.parent
        return parent_dir.exists() and os.access(parent_dir, os.W_OK)
    except (OSError, ValueError):
        return False 