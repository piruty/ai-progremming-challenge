#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像リサイズ & 圧縮アプリ
ドラッグ&ドロップ対応のGUIアプリケーション
"""

import tkinterdnd2 as tkdnd
from pathlib import Path
from os import environ
from sys import base_prefix

from models.settings import AppSettings
from views.main_window import MainWindow
from controllers.app_controller import AppController

def main():

    # environ["TCL_LIBRARY"] = str(Path(base_prefix) / "tcl" / "tcl8.6")
    # environ["TK_LIBRARY"] = str(Path(base_prefix) / "tcl" / "tk8.6")

    # print(environ["TCL_LIBRARY"])
    # print(environ["TK_LIBRARY"])
    """メイン関数"""
    # ルートウィンドウを作成
    root = tkdnd.Tk()
    
    try:
        # 設定を初期化
        settings = AppSettings()
        
        # ビューを作成
        window = MainWindow(root, settings)
        
        # コントローラーを作成
        controller = AppController(window, settings)
        
        # アプリケーションを開始
        root.mainloop()
        
    except Exception as e:
        print(f"アプリケーションエラー: {e}")
    finally:
        # クリーンアップ処理
        try:
            if 'controller' in locals():
                controller.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main() 