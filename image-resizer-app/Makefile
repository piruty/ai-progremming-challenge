# 画像リサイズ & 圧縮アプリ - Makefile
# 開発作業を効率化するためのタスクランナー

.PHONY: help install run test test-settings test-image test-file test-all lint format type-check quality clean deps-update

# デフォルトターゲット（ヘルプを表示）
help:
	@echo "🖼️  画像リサイズ & 圧縮アプリ - 開発用Makefile"
	@echo ""
	@echo "📋 利用可能なコマンド:"
	@echo "  install       - プロジェクトの初期セットアップ（uv sync）"
	@echo "  run          - アプリケーションを実行"
	@echo "  test         - 全テストを実行"
	@echo "  test-settings - 設定モデルのテストのみ実行"
	@echo "  test-image   - 画像処理のテストのみ実行"
	@echo "  test-file    - ファイルユーティリティのテストのみ実行"
	@echo "  test-all     - テスト + カバレッジレポート付き"
	@echo "  lint         - コード品質チェック（flake8）"
	@echo "  format       - コードフォーマット（black + isort）"
	@echo "  type-check   - 型チェック（mypy）"
	@echo "  quality      - 全品質チェック（lint + format + type-check）"
	@echo "  deps-update  - 依存関係を更新"
	@echo "  clean        - 一時ファイルをクリーンアップ"
	@echo ""
	@echo "🚀 基本的な使用方法:"
	@echo "  1. make install  - 初回セットアップ"
	@echo "  2. make run      - アプリケーション実行"
	@echo "  3. make test     - テスト実行"

# プロジェクトの初期セットアップ
install:
	@echo "📦 依存関係をインストール中..."
	uv sync
	@echo "✅ インストール完了！"

# アプリケーションを実行
run:
	@echo "🚀 アプリケーションを起動中..."
	uv run python main.py

# 全テストを実行
test:
	@echo "🧪 全テストを実行中..."
	uv run python run_tests.py

# 設定モデルのテストのみ実行
test-settings:
	@echo "⚙️  設定モデルのテストを実行中..."
	uv run python run_tests.py test_settings

# 画像処理のテストのみ実行
test-image:
	@echo "🖼️  画像処理のテストを実行中..."
	uv run python run_tests.py test_image_processor

# ファイルユーティリティのテストのみ実行
test-file:
	@echo "📁 ファイルユーティリティのテストを実行中..."
	uv run python run_tests.py test_file_utils

# テスト + カバレッジレポート付き（coverage.pyが必要）
test-all:
	@echo "🧪 テスト + カバレッジレポートを実行中..."
	@if command -v coverage >/dev/null 2>&1; then \
		uv run coverage run run_tests.py; \
		uv run coverage report; \
		uv run coverage html; \
		echo "📊 カバレッジレポートが htmlcov/ に生成されました"; \
	else \
		echo "⚠️  coverageがインストールされていません。通常のテストを実行します。"; \
		uv run python run_tests.py; \
	fi

# コード品質チェック（flake8）
lint:
	@echo "🔍 コード品質をチェック中（flake8）..."
	@if command -v flake8 >/dev/null 2>&1 || uv run flake8 --version >/dev/null 2>&1; then \
		uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; \
		uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics; \
	else \
		echo "⚠️  flake8がインストールされていません。'uv sync --group dev'でインストールしてください。"; \
	fi

# コードフォーマット（black + isort）
format:
	@echo "🎨 コードをフォーマット中..."
	@if command -v isort >/dev/null 2>&1 || uv run isort --version >/dev/null 2>&1; then \
		uv run isort .; \
		if command -v black >/dev/null 2>&1 || uv run black --version >/dev/null 2>&1; then \
			uv run black .; \
			echo "✅ フォーマット完了！"; \
		else \
			echo "⚠️  blackがインストールされていません。"; \
		fi; \
	else \
		echo "⚠️  isort/blackがインストールされていません。'uv sync --group dev'でインストールしてください。"; \
	fi

# 型チェック（mypy）
type-check:
	@echo "🔬 型チェック中（mypy）..."
	@if command -v mypy >/dev/null 2>&1 || uv run mypy --version >/dev/null 2>&1; then \
		uv run mypy . --ignore-missing-imports; \
	else \
		echo "⚠️  mypyがインストールされていません。'uv sync --group dev'でインストールしてください。"; \
	fi

# 全品質チェック
quality: lint format type-check
	@echo "✅ 全品質チェック完了！"

# 依存関係を更新
deps-update:
	@echo "📦 依存関係を更新中..."
	uv sync --upgrade
	@echo "✅ 依存関係更新完了！"

# 一時ファイルをクリーンアップ
clean:
	@echo "🧹 一時ファイルをクリーンアップ中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ クリーンアップ完了！"

# 開発環境のセットアップ（全体）
setup: install
	@echo "🛠️  開発環境のセットアップ中..."
	@make test
	@echo "✅ 開発環境のセットアップ完了！"

# リリース前チェック
pre-commit: clean quality test
	@echo "🚀 リリース前チェック完了！コードは本番準備完了です。"

# プロジェクト統計情報
stats:
	@echo "📊 プロジェクト統計情報:"
	@echo "Python ファイル数: $$(find . -maxdepth 3 -name '*.py' -not -path './.venv/*' -not -path './venv/*' | wc -l)"
	@echo "コード行数:"
	@find . -maxdepth 3 -name '*.py' -not -path './.venv/*' -not -path './venv/*' -exec wc -l {} + | tail -1
	@echo "テストファイル数: $$(find tests/ -name 'test_*.py' 2>/dev/null | wc -l)"

# ドキュメント生成（Sphinx等が設定されている場合）
docs:
	@echo "📚 ドキュメントを生成中..."
	@if [ -f "docs/Makefile" ]; then \
		cd docs && make html; \
		echo "✅ ドキュメント生成完了！docs/_build/html/ を確認してください"; \
	else \
		echo "📖 README.md と code.md を参照してください"; \
	fi

# デバッグ用：環境情報表示
env-info:
	@echo "🔧 環境情報:"
	@echo "Python バージョン: $$(python --version)"
	@echo "uv バージョン: $$(uv --version)"
	@echo "現在のディレクトリ: $$(pwd)"
	@echo "仮想環境: $${VIRTUAL_ENV:-なし}" 