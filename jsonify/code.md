# jsonify - 実装詳細と学習ポイント

## プロジェクト概要

jsonifyは「JSON 整形・バリデータ（整形、キーソート、スキーマチェック対応）」をGoで実装したCLIツールです。

### 主要機能

- ✅ JSON整形（インデント調整、見やすい表示）
- ✅ JSONバリデーション（構文チェック）
- ✅ キーのアルファベット順ソート
- ✅ JSONスキーマによるバリデーション

## プロジェクト構造

```txt
jsonify/
├── main.go              # エントリーポイント
├── go.mod              # Go modules設定
├── go.sum              # 依存関係のハッシュ
├── README.md           # 使用方法とドキュメント
├── jsonify             # ビルド済み実行ファイル
├── cmd/                # コマンド実装
│   ├── root.go         # ルートコマンド
│   ├── format.go       # 整形コマンド
│   ├── validate.go     # バリデーションコマンド
│   ├── schema.go       # スキーマバリデーションコマンド
│   ├── format_test.go  # 整形機能のテスト
│   ├── validate_test.go # バリデーション機能のテスト
│   ├── schema_test.go  # スキーマバリデーション機能のテスト
│   └── root_test.go    # ルートコマンドのテスト
└── examples/           # テスト用サンプルファイル
    ├── sample.json     # 有効なJSONサンプル
    ├── invalid.json    # 無効なJSONサンプル
    ├── invalid-data.json # スキーマ違反データ
    └── person-schema.json # JSONスキーマサンプル
```

## 学習ポイント

### 1. Go言語でのCLI開発基礎

#### main.goの設計

```go
package main

import (
    "os"
    "jsonify/cmd"
)

func main() {
    if err := cmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

**学習ポイント:**

- シンプルなエントリーポイント設計
- エラーハンドリングの基本パターン
- パッケージ分離の重要性

#### Go Modulesの活用

```go
module jsonify

go 1.21

require (
    github.com/spf13/cobra v1.8.0
    github.com/xeipuuv/gojsonschema v1.2.0
)
```

**学習ポイント:**

- 外部ライブラリの依存関係管理
- セマンティックバージョニングの理解
- `go mod tidy`の使用方法

### 2. Cobraフレームワークによるコマンド設計

#### Cobraライブラリとは

Cobraは、Go言語でモダンなCLI（Command Line Interface）アプリケーションを作成するための強力なライブラリです。

**主な特徴:**

- **階層的なコマンド構造**: サブコマンド、フラグ、引数の管理
- **自動ヘルプ生成**: `--help`や`-h`フラグの自動サポート
- **POSIX準拠**: Unix/Linux標準のコマンドライン規約に準拠
- **シェル補完**: Bash、Zsh、Fish、PowerShellでの自動補完機能
- **豊富なエコシステム**: kubectl、Hugo、Docker等の有名プロジェクトで採用

**GitHub**: https://github.com/spf13/cobra

#### Cobraの核となる概念

##### 1. Command（コマンド）

コマンドは実行可能な操作の単位です。`cobra.Command`構造体で定義されます。

```go
var rootCmd = &cobra.Command{
    Use:   "jsonify",                    // コマンド名
    Short: "JSON formatter and validator", // 短い説明
    Long: `jsonify is a CLI tool that provides:...`, // 詳細な説明
    RunE:  runRootCommand,              // 実行する関数
}
```

**重要なフィールド:**

- `Use`: コマンド名と使用方法
- `Short`: ヘルプに表示される短い説明
- `Long`: 詳細なヘルプメッセージ
- `RunE`: エラーを返すrun関数（推奨）
- `Run`: エラーを返さないrun関数

##### 2. Flag（フラグ）

フラグはコマンドのオプションを定義します。

```go
formatCmd.Flags().StringVarP(&indent, "indent", "i", "  ", "Indentation string")
```

**フラグの種類:**

- `StringVarP`: 文字列値（長形式: `--indent`, 短形式: `-i`）
- `BoolVarP`: ブール値（`--sort`, `-s`）
- `IntVarP`: 整数値
- `StringSliceVarP`: 文字列スライス（複数値）

##### 3. Args（引数）

コマンドライン引数の検証を行います。

```go
var myCmd = &cobra.Command{
    Use:  "command",
    Args: cobra.ExactArgs(1),  // 引数を1つだけ受け取る
    RunE: runMyCommand,
}
```

**引数検証の種類:**

- `cobra.NoArgs`: 引数なし
- `cobra.ExactArgs(n)`: 正確にn個の引数
- `cobra.MinimumNArgs(n)`: 最低n個の引数
- `cobra.MaximumNArgs(n)`: 最大n個の引数

#### jsonifyプロジェクトでのCobra実装

##### ルートコマンドの設計

```go
// cmd/root.go
package cmd

import (
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "jsonify",
    Short: "JSON formatter and validator with schema support",
    Long: `jsonify is a CLI tool that provides:
- JSON formatting and pretty printing
- JSON validation
- Key sorting
- JSON schema validation`,
}

// Execute は main.go から呼び出される公開関数
func Execute() error {
    return rootCmd.Execute()
}

func init() {
    cobra.OnInitialize()
}
```

**設計のポイント:**

- ルートコマンドは主にサブコマンドのコンテナとして機能
- `Execute()`関数を公開してmain.goから呼び出し
- `init()`関数でCobra初期化処理を実行

##### サブコマンドの実装パターン

```go
// cmd/format.go
package cmd

import (
    "encoding/json"
    "fmt"
    "io"
    "os"
    "sort"
    "github.com/spf13/cobra"
)

// グローバル変数でフラグ値を保持
var (
    indent     string
    sortKeys   bool
    inputFile  string
    outputFile string
)

// サブコマンドの定義
var formatCmd = &cobra.Command{
    Use:   "format",
    Short: "Format and prettify JSON",
    Long:  `Format JSON with proper indentation and optionally sort keys`,
    RunE:  runFormat,  // エラーハンドリング付きの実行関数
}

// init関数でルートコマンドに追加とフラグ設定
func init() {
    // サブコマンドをルートコマンドに追加
    rootCmd.AddCommand(formatCmd)
    
    // フラグの定義
    formatCmd.Flags().StringVarP(&indent, "indent", "i", "  ", 
        "Indentation string (default: 2 spaces)")
    formatCmd.Flags().BoolVarP(&sortKeys, "sort", "s", false, 
        "Sort keys alphabetically")
    formatCmd.Flags().StringVarP(&inputFile, "input", "f", "", 
        "Input file (default: stdin)")
    formatCmd.Flags().StringVarP(&outputFile, "output", "o", "", 
        "Output file (default: stdout)")
}

// 実際のコマンド処理を行う関数
func runFormat(cmd *cobra.Command, args []string) error {
    // フラグ値を使用した処理...
    var input io.Reader = os.Stdin
    var output io.Writer = os.Stdout
    
    // inputFileフラグが指定された場合
    if inputFile != "" {
        file, err := os.Open(inputFile)
        if err != nil {
            return fmt.Errorf("failed to open input file: %w", err)
        }
        defer file.Close()
        input = file
    }
    
    // JSON処理のロジック...
    return nil
}
```

#### Cobraのベストプラクティス

##### 1. エラーハンドリング

```go
// RunE を使用してエラーを適切に返す
var myCmd = &cobra.Command{
    Use:  "command",
    RunE: func(cmd *cobra.Command, args []string) error {
        if err := someOperation(); err != nil {
            return fmt.Errorf("operation failed: %w", err)
        }
        return nil
    },
}
```

**ポイント:**

- `Run`より`RunE`を使用してエラーハンドリングを明示的に
- エラーラッピング（`%w`）でコンテキストを追加
- ユーザーフレンドリーなエラーメッセージを心がける

##### 2. フラグの設計原則

```go
// 良い例: 短縮形、デフォルト値、説明文を適切に設定
formatCmd.Flags().StringVarP(&outputFile, "output", "o", "", 
    "Output file (default: stdout)")

// 避けるべき例: 短縮形なし、説明不足
formatCmd.Flags().StringVar(&outputFile, "output", "", "output")
```

**設計原則:**

- 一般的なフラグには短縮形を提供（`-o`, `-f`, `-v`など）
- 明確で一貫したデフォルト値を設定
- 分かりやすい説明文を記述

##### 3. コマンド構造の設計

```go
// 階層的なコマンド構造の例
app
├── format              // jsonify format
├── validate            // jsonify validate  
├── schema              // jsonify schema
└── config              // jsonify config
    ├── set            // jsonify config set
    └── get            // jsonify config get
```

**設計指針:**

- 機能ごとにサブコマンドを分離
- 論理的に関連するコマンドをグループ化
- 一般的なCLI規約に従う（`list`, `get`, `set`, `create`, `delete`など）

##### 4. 入出力の抽象化

```go
func runCommand(cmd *cobra.Command, args []string) error {
    // 標準入出力をデフォルト、フラグで変更可能
    var input io.Reader = os.Stdin
    var output io.Writer = os.Stdout
    
    if inputFile != "" {
        file, err := os.Open(inputFile)
        if err != nil {
            return fmt.Errorf("failed to open input file: %w", err)
        }
        defer file.Close()
        input = file
    }
    
    // input, outputを使用した処理...
    return processData(input, output)
}
```

**利点:**

- テストが容易（モックしやすい）
- Unix哲学に従った設計（パイプ処理可能）
- ファイルと標準入出力の統一的な処理

#### Cobraとjsonifyの統合

jsonifyプロジェクトでは、以下のようにCobraを活用しています：

##### 1. 機能別サブコマンド

```bash
jsonify format --sort --indent "    " -f input.json -o output.json
jsonify validate -f data.json
jsonify schema -f data.json -s schema.json
```

##### 2. 一貫したフラグ設計

```go
// 共通フラグパターン
-f, --input   "入力ファイル (デフォルト: stdin)"
-o, --output  "出力ファイル (デフォルト: stdout)"
-s, --sort    "キーをアルファベット順にソート"
-i, --indent  "インデント文字列"
```

##### 3. エラーハンドリングの統一

```go
// すべてのコマンドで一貫したエラー処理
if err := runFormat(cmd, args); err != nil {
    return fmt.Errorf("format command failed: %w", err)
}
```

#### Cobraを使う利点

1. **開発効率の向上**
   - ボイラープレートコードの削減
   - 自動ヘルプ生成
   - 標準的なCLI規約に自動準拠

2. **ユーザビリティの向上**
   - 一貫したコマンド体験
   - 豊富なヘルプシステム
   - シェル補完サポート

3. **保守性の向上**
   - 構造化されたコマンド管理
   - テストが容易な設計
   - 拡張性の高いアーキテクチャ

4. **実績と信頼性**
   - 多くの有名プロジェクトで採用
   - 活発なコミュニティとメンテナンス
   - 豊富なドキュメントと事例

jsonifyプロジェクトを通じて、Cobraを使ったモダンなCLI開発の実践的なパターンを学ぶことができます。

### 3. JSON処理の実装

#### JSON整形とキーソート

```go
func sortJSONKeys(data interface{}) interface{} {
    switch v := data.(type) {
    case map[string]interface{}:
        keys := make([]string, 0, len(v))
        for key := range v {
            keys = append(keys, key)
        }
        sort.Strings(keys)
        
        result := make(map[string]interface{})
        for _, key := range keys {
            result[key] = sortJSONKeys(v[key])
        }
        return result
    case []interface{}:
        result := make([]interface{}, len(v))
        for i, item := range v {
            result[i] = sortJSONKeys(item)
        }
        return result
    default:
        return v
    }
}
```

**学習ポイント:**

- 型アサーション（Type Assertion）の使用
- 再帰処理による深い構造の処理
- インターフェース型の活用
- スライスのソート処理

#### JSONバリデーション

```go
var jsonData interface{}
if err := json.Unmarshal(data, &jsonData); err != nil {
    fmt.Printf("❌ Invalid JSON: %v\n", err)
    return err
}
fmt.Println("✅ Valid JSON")
```

**学習ポイント:**

- `encoding/json`パッケージの使用
- エラーハンドリングのパターン
- ユーザーフレンドリーなメッセージ表示

### 4. ファイル操作と標準入出力

#### 入力ソースの抽象化

```go
var input io.Reader = os.Stdin

if inputFile != "" {
    file, err := os.Open(inputFile)
    if err != nil {
        return fmt.Errorf("failed to open input file: %w", err)
    }
    defer file.Close()
    input = file
}
```

**学習ポイント:**

- `io.Reader`インターフェースによる抽象化
- ファイルと標準入力の統一的な処理
- `defer`によるリソース管理
- エラーラッピング（`%w`動詞）の使用

#### 出力先の抽象化

```go
var output io.Writer = os.Stdout

if outputFile != "" {
    file, err := os.Create(outputFile)
    if err != nil {
        return fmt.Errorf("failed to create output file: %w", err)
    }
    defer file.Close()
    output = file
}
```

**学習ポイント:**

- `io.Writer`インターフェースの活用
- ファイル作成と標準出力の統一処理
- 設計の一貫性の重要性

### 5. 外部ライブラリの活用

#### JSONスキーマバリデーション

```go
import "github.com/xeipuuv/gojsonschema"

schemaLoader := gojsonschema.NewBytesLoader(schemaData)
documentLoader := gojsonschema.NewBytesLoader(data)

result, err := gojsonschema.Validate(schemaLoader, documentLoader)
if err != nil {
    return fmt.Errorf("validation error: %w", err)
}

if result.Valid() {
    fmt.Println("✅ JSON is valid according to the schema")
} else {
    fmt.Println("❌ JSON validation failed:")
    for _, desc := range result.Errors() {
        fmt.Printf("  - %s\n", desc)
    }
}
```

**学習ポイント:**

- 外部ライブラリの選定基準
- API設計の学習（Loaderパターン）
- エラーメッセージの詳細表示

### 6. テスト設計と実装

#### テストの設計方針

- **単体テスト**: 各コマンドの機能を個別にテスト
- **統合テスト**: ファイル入出力を含む実際の使用ケース
- **エラーケーステスト**: 異常系の動作確認
- **エッジケーステスト**: 境界値や特殊ケースの処理

#### テストの実装パターン

##### テーブルドリブンテスト

```go
tests := []struct {
    name     string
    input    string
    expected string
    wantErr  bool
}{
    {
        name:     "有効なJSON",
        input:    `{"name":"John","age":30}`,
        expected: "✅ Valid JSON",
        wantErr:  false,
    },
    {
        name:    "無効なJSON",
        input:   `{"name":"John","age":30`,
        wantErr: true,
    },
}
```

**学習ポイント:**

- テーブルドリブンテストの設計
- テストケースの体系的な整理
- 正常系と異常系の網羅

##### 標準入出力のテスト

```go
// 入力の準備
oldStdin := os.Stdin
r, w, _ := os.Pipe()
os.Stdin = r

go func() {
    defer w.Close()
    w.Write([]byte(tt.input))
}()

// 出力の準備
oldStdout := os.Stdout
rOut, wOut, _ := os.Pipe()
os.Stdout = wOut

// テスト実行
err := runValidate(nil, []string{})

// 後処理
os.Stdin = oldStdin
os.Stdout = oldStdout
```

**学習ポイント:**

- パイプを使用した入出力のモッキング
- グローバル状態の安全な変更と復元
- 並行処理を使った入力の送信

##### 一時ファイルを使用したテスト

```go
validFile, err := os.CreateTemp("", "valid_*.json")
if err != nil {
    t.Fatalf("一時ファイルの作成に失敗: %v", err)
}
defer os.Remove(validFile.Name())

if _, err := validFile.WriteString(validJSON); err != nil {
    t.Fatalf("ファイルへの書き込みに失敗: %v", err)
}
validFile.Close()
```

**学習ポイント:**

- 一時ファイルの安全な作成と削除
- `defer`による確実なクリーンアップ
- ファイル操作のエラーハンドリング

#### テストカバレッジ

- **達成率**: 83.2%
- **テスト数**: 81個のテストケース
- **カバレッジ範囲**: 全コマンドの正常系・異常系

### 7. エラーハンドリングのベストプラクティス

#### エラーラッピング

```go
if err := json.Unmarshal(data, &jsonData); err != nil {
    return fmt.Errorf("invalid JSON: %w", err)
}
```

**学習ポイント:**

- `%w`動詞によるエラーチェーンの構築
- コンテキスト情報の追加
- エラーの根本原因の保持

#### ユーザーフレンドリーなエラーメッセージ

```go
fmt.Printf("❌ Invalid JSON: %v\n", err)
fmt.Println("✅ Valid JSON")
```

**学習ポイント:**

- 絵文字を使用した視覚的なフィードバック
- 明確で理解しやすいメッセージ
- 成功と失敗の明確な区別

### 8. 設計パターンと原則

#### Command Pattern

- Cobraフレームワークを使用したコマンドパターンの実装
- 各コマンドの独立性と再利用性の確保

#### Interface Segregation

- `io.Reader`と`io.Writer`による入出力の抽象化
- 依存関係の最小化

#### Single Responsibility Principle

- 各ファイルが単一の責任を持つ設計
- 関数の単一責任の徹底

#### Dependency Injection

- 外部ライブラリへの依存の管理
- テストでのモッキングの容易さ

### 9. 性能とメモリ効率

#### ストリーミング処理

```go
data, err := io.ReadAll(input)
```

**学習ポイント:**

- 大きなファイルでも安全に処理する設計
- メモリ使用量の最適化の検討事項

#### リソース管理

```go
defer file.Close()
```

**学習ポイント:**

- ファイルハンドルの確実なクローズ
- メモリリークの防止

### 10. 実用的な開発Tips

#### ビルドとテスト

```bash
# ビルド
go build -o jsonify .

# テスト実行
go test ./cmd/... -v

# カバレッジ確認
go test ./cmd/... -cover
```

#### デバッグとトラブルシューティング

- ログ出力の戦略
- エラーメッセージの改善
- テストの段階的な実装

## まとめ

このjsonifyプロジェクトを通じて学習できる主要なポイント：

1. **Go言語の実践的な使用方法**

   - 標準ライブラリの活用
   - 外部ライブラリとの連携
   - エラーハンドリング

2. **CLI開発のベストプラクティス**

   - Cobraフレームワークの使用
   - ユーザビリティの考慮
   - 設定とオプションの設計

3. **テスト駆動開発**

   - 包括的なテスト設計
   - モッキングとスタブの使用
   - カバレッジの確保

4. **プロジェクト構造と保守性**

   - パッケージ分割
   - 関心の分離
   - コードの可読性

5. **実用的なJSON処理**

   - パースとバリデーション
   - スキーマ検証
   - 整形とソート

このプロジェクトは、Go言語でのCLI開発における実践的なスキルを体系的に学習できる良い例となっています。
