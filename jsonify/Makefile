# jsonify - Makefile
# JSON formatter and validator CLI tool

# 変数定義
APP_NAME = jsonify
GO_FILES = $(shell find . -name "*.go" -type f -not -path "./vendor/*")
MODULE_NAME = jsonify

# デフォルトターゲット
.DEFAULT_GOAL := help

# バイナリビルド
.PHONY: build
build: ## プロジェクトをビルドして実行可能ファイルを作成
	@echo "🔨 Building $(APP_NAME)..."
	go build -o $(APP_NAME) .
	@echo "✅ Build completed: $(APP_NAME)"

# テスト実行
.PHONY: test
test: ## 全てのテストを実行
	@echo "🧪 Running tests..."
	go test ./cmd/... -v
	@echo "✅ Tests completed"

# テストカバレッジ
.PHONY: test-coverage
test-coverage: ## テストカバレッジを表示
	@echo "📊 Running tests with coverage..."
	go test ./cmd/... -cover -v
	@echo "✅ Coverage analysis completed"

# テストカバレッジ詳細（HTMLレポート）
.PHONY: test-coverage-html
test-coverage-html: ## HTMLカバレッジレポートを生成
	@echo "📊 Generating HTML coverage report..."
	go test ./cmd/... -coverprofile=coverage.out
	go tool cover -html=coverage.out -o coverage.html
	@echo "✅ HTML coverage report generated: coverage.html"

# Go実行（developmentモード）
.PHONY: run
run: ## go runでプロジェクトを実行（引数: ARGS）
	@echo "🚀 Running with go run..."
	go run . $(ARGS)

# サンプル実行
.PHONY: run-examples
run-examples: build ## サンプルファイルを使用してコマンドの動作を確認
	@echo "🎯 Running examples..."
	@echo "--- JSON Formatting ---"
	./$(APP_NAME) format -f examples/sample.json -s
	@echo
	@echo "--- JSON Validation ---"
	./$(APP_NAME) validate -f examples/sample.json
	./$(APP_NAME) validate -f examples/invalid.json
	@echo
	@echo "--- Schema Validation ---"
	./$(APP_NAME) schema -f examples/sample.json -s examples/person-schema.json
	@echo "✅ Examples completed"

# 依存関係の整理
.PHONY: tidy
tidy: ## go.modファイルの依存関係を整理
	@echo "🧹 Tidying dependencies..."
	go mod tidy
	@echo "✅ Dependencies tidied"

# ベンダリング
.PHONY: vendor
vendor: ## 依存関係をvendorディレクトリにダウンロード
	@echo "📦 Downloading vendor dependencies..."
	go mod vendor
	@echo "✅ Vendor dependencies downloaded"

# クリーンアップ
.PHONY: clean
clean: ## ビルド成果物を削除
	@echo "🧹 Cleaning up..."
	rm -f $(APP_NAME)
	rm -f coverage.out
	rm -f coverage.html
	rm -rf vendor/
	@echo "✅ Cleanup completed"

# インストール
.PHONY: install
install: ## バイナリを$GOPATH/binにインストール
	@echo "💿 Installing $(APP_NAME)..."
	go install .
	@echo "✅ $(APP_NAME) installed to $GOPATH/bin"

# フォーマット
.PHONY: fmt
fmt: ## コードフォーマットを実行
	@echo "🎨 Formatting code..."
	go fmt ./...
	@echo "✅ Code formatted"

# Lint
.PHONY: lint
lint: ## golangci-lintを実行（golangci-lintが必要）
	@echo "🔍 Running linter..."
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run; \
		echo "✅ Linting completed"; \
	else \
		echo "⚠️  golangci-lint not found. Install it with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

# ベンチマーク
.PHONY: bench
bench: ## ベンチマークテストを実行
	@echo "⚡ Running benchmarks..."
	go test -bench=. -benchmem ./cmd/...
	@echo "✅ Benchmarks completed"

# 全体チェック
.PHONY: check
check: fmt lint test ## フォーマット、Lint、テストを順次実行
	@echo "✅ All checks passed"

# 開発用のクイックビルド
.PHONY: dev
dev: ## 開発用：フォーマット、ビルド、簡単なテストを実行
	@echo "🚀 Development build..."
	$(MAKE) fmt
	$(MAKE) build
	$(MAKE) test
	@echo "✅ Development build completed"

# リリース用のビルド
.PHONY: release
release: ## リリース用：全チェックを実行してからビルド
	@echo "🚀 Release build..."
	$(MAKE) clean
	$(MAKE) check
	$(MAKE) build
	@echo "✅ Release build completed"

# ヘルプ
.PHONY: help
help: ## このヘルプメッセージを表示
	@echo "jsonify - JSON formatter and validator"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make build                 # プロジェクトをビルド"
	@echo "  make test                  # テストを実行"
	@echo "  make run ARGS='--help'     # ヘルプを表示"
	@echo "  make run ARGS='format -f examples/sample.json -s'  # サンプルファイルを整形"
	@echo "  make run-examples          # 全てのサンプルを実行" 