# Makefile for regrep - 正規表現grep風コマンド

# 変数定義
BINARY_NAME := regrep
GO_FILES := $(shell find . -name "*.go" -type f)
BUILD_DIR := build
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS := -ldflags "-X main.version=$(VERSION)"

# デフォルトターゲット
.DEFAULT_GOAL := build

# ヘルプ表示
.PHONY: help
help: ## このヘルプを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ビルド
.PHONY: build
build: $(BUILD_DIR)/$(BINARY_NAME) ## バイナリをビルド

$(BUILD_DIR)/$(BINARY_NAME): $(GO_FILES)
	@echo "Building $(BINARY_NAME)..."
	@mkdir -p $(BUILD_DIR)
	go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) .

# 開発用ビルド（現在ディレクトリに出力）
.PHONY: build-dev
build-dev: ## 開発用バイナリをビルド（現在ディレクトリ）
	@echo "Building $(BINARY_NAME) for development..."
	go build $(LDFLAGS) -o $(BINARY_NAME) .

# 実行
.PHONY: run
run: build-dev ## プログラムを実行（使用例を表示）
	@echo "=== regrep 使用例 ==="
	@echo "1. ヘルプ表示:"
	./$(BINARY_NAME) -h
	@echo
	@echo "2. test.txtからfuncを検索:"
	./$(BINARY_NAME) "func" test.txt
	@echo
	@echo "3. 行番号付きでfmt.Printを検索:"
	./$(BINARY_NAME) -n "fmt\.Print" test.txt

# カスタム実行（引数付き）
.PHONY: run-with
run-with: build-dev ## プログラムを引数付きで実行 (make run-with ARGS="pattern file")
	./$(BINARY_NAME) $(ARGS)

# テスト
.PHONY: test
test: ## テストを実行
	@echo "Running tests..."
	go test -v ./...

# テスト（カバレッジ付き）
.PHONY: test-coverage
test-coverage: ## テストをカバレッジ付きで実行
	@echo "Running tests with coverage..."
	go test -v -cover ./...
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "カバレッジレポートを coverage.html に出力しました"

# ベンチマーク
.PHONY: bench
bench: ## ベンチマークテストを実行
	@echo "Running benchmarks..."
	go test -bench=. -benchmem ./...

# コードフォーマット
.PHONY: fmt
fmt: ## コードをフォーマット
	@echo "Formatting code..."
	go fmt ./...

# コード解析
.PHONY: vet
vet: ## コードを解析
	@echo "Vetting code..."
	go vet ./...

# リント
.PHONY: lint
lint: ## コードをリント（golangci-lintが必要）
	@echo "Linting code..."
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run; \
	else \
		echo "golangci-lint not found. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

# 依存関係の整理
.PHONY: tidy
tidy: ## go.modを整理
	@echo "Tidying dependencies..."
	go mod tidy

# すべてのチェックを実行
.PHONY: check
check: fmt vet test ## フォーマット・解析・テストを実行

# インストール
.PHONY: install
install: ## システムにインストール
	@echo "Installing $(BINARY_NAME)..."
	go install $(LDFLAGS) .

# クリーンアップ
.PHONY: clean
clean: ## 生成されたファイルを削除
	@echo "Cleaning up..."
	@rm -rf $(BUILD_DIR)
	@rm -f $(BINARY_NAME)
	@rm -f coverage.out coverage.html

# クロスコンパイル
.PHONY: build-all
build-all: ## 各プラットフォーム用にビルド
	@echo "Building for multiple platforms..."
	@mkdir -p $(BUILD_DIR)
	@for os in linux darwin windows; do \
		for arch in amd64 arm64; do \
			if [ "$$os" = "windows" ]; then \
				ext=".exe"; \
			else \
				ext=""; \
			fi; \
			echo "Building for $$os/$$arch..."; \
			GOOS=$$os GOARCH=$$arch go build $(LDFLAGS) \
				-o $(BUILD_DIR)/$(BINARY_NAME)-$$os-$$arch$$ext .; \
		done \
	done

# リリース用ビルド
.PHONY: release
release: clean test build-all ## リリース用ビルド（テスト後、全プラットフォーム）
	@echo "Release build completed in $(BUILD_DIR)/"
	@ls -la $(BUILD_DIR)/

# 開発環境セットアップ
.PHONY: setup
setup: ## 開発環境をセットアップ
	@echo "Setting up development environment..."
	go mod download
	@if ! command -v golangci-lint >/dev/null 2>&1; then \
		echo "Installing golangci-lint..."; \
		go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest; \
	fi
	@echo "Development environment is ready!"

# デモ実行
.PHONY: demo
demo: build-dev ## デモを実行
	@echo "=== regrep デモンストレーション ==="
	@echo
	@echo "1. ヘルプの表示:"
	@echo "$ ./$(BINARY_NAME) -h"
	@./$(BINARY_NAME) -h
	@echo
	@echo "2. test.txtから'func'を検索:"
	@echo "$ ./$(BINARY_NAME) 'func' test.txt"
	@./$(BINARY_NAME) "func" test.txt
	@echo
	@echo "3. 行番号付きで'fmt'を検索:"
	@echo "$ ./$(BINARY_NAME) -n 'fmt' test.txt"
	@./$(BINARY_NAME) -n "fmt" test.txt
	@echo
	@echo "4. 大文字小文字を無視して'ERROR'を検索:"
	@echo "$ ./$(BINARY_NAME) -i 'ERROR' test.txt"
	@./$(BINARY_NAME) -i "ERROR" test.txt
	@echo
	@echo "5. パイプでの使用例:"
	@echo "$ /bin/cat test.txt | ./$(BINARY_NAME) 'package'"
	@/bin/cat test.txt | ./$(BINARY_NAME) "package"

# 情報表示
.PHONY: info
info: ## プロジェクト情報を表示
	@echo "プロジェクト情報:"
	@echo "  名前: $(BINARY_NAME)"
	@echo "  バージョン: $(VERSION)"
	@echo "  Goバージョン: $(shell go version)"
	@echo "  ビルドディレクトリ: $(BUILD_DIR)"
	@echo "  Goファイル数: $(shell echo $(GO_FILES) | wc -w)" 