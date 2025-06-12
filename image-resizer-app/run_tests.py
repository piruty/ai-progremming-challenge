#!/usr/bin/env python3
"""
全テスト実行スクリプト
"""

import sys
import unittest
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def run_all_tests():
    """すべてのテストを実行"""
    # テストディレクトリからテストを発見
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果を返す
    return result.wasSuccessful()


def run_specific_test(test_module):
    """特定のテストモジュールを実行"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 特定のテストモジュールを実行
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # すべてのテストを実行
        success = run_all_tests()
    
    # 終了コードを設定
    sys.exit(0 if success else 1) 