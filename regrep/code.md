# main.go コード解説

このドキュメントでは、正規表現grep風コマンド「regrep」の実装について詳しく解説します。

## 全体構成

```go
package main
```

メインパッケージとして実行可能バイナリを生成します。

## インポート

```go
import (
    "bufio"      // バッファ付きI/O操作
    "flag"       // コマンドライン引数解析
    "fmt"        // フォーマット済みI/O
    "io"         // 基本的なI/Oプリミティブ
    "os"         // オペレーティングシステムインターフェース
    "path/filepath" // ファイルパス操作
    "regexp"     // 正規表現
    "strings"    // 文字列操作
)
```

各パッケージは以下の目的で使用されています：

- `bufio`: ファイル読み込みの効率化
- `flag`: `-n`, `-i`などのオプション解析
- `fmt`: 出力とエラーメッセージ
- `io`: Reader抽象化
- `os`: ファイル操作と標準入出力
- `path/filepath`: 再帰的ディレクトリ探索
- `regexp`: 正規表現エンジン
- `strings`: 効率的な文字列構築

## Config構造体

```go
type Config struct {
    Pattern    string   // 検索パターン（正規表現）
    Files      []string // 処理対象ファイル一覧
    ShowLine   bool     // 行番号表示フラグ (-n)
    IgnoreCase bool     // 大文字小文字無視フラグ (-i)
    Recursive  bool     // 再帰的検索フラグ (-r)
    Invert     bool     // 反転検索フラグ (-v)
    Count      bool     // カウントモードフラグ (-c)
    Help       bool     // ヘルプ表示フラグ (-h)
}
```

すべてのコマンドオプションと設定を一つの構造体で管理し、関数間での設定の受け渡しを簡潔にしています。

## main関数

```go
func main() {
    config := parseFlags()
    
    if config.Help {
        printUsage()
        return
    }
    
    if config.Pattern == "" {
        fmt.Fprintf(os.Stderr, "エラー: 検索パターンが指定されていません\n")
        printUsage()
        os.Exit(1)
    }
```

### 正規表現コンパイル

```go
// 正規表現をコンパイル
var re *regexp.Regexp
var err error

// 正規表現として解釈を試す
if config.IgnoreCase {
    re, err = regexp.Compile("(?i)" + config.Pattern)
} else {
    re, err = regexp.Compile(config.Pattern)
}
if err != nil {
    fmt.Fprintf(os.Stderr, "エラー: 無効な正規表現 '%s': %v\n", config.Pattern, err)
    os.Exit(1)
}
```

**ポイント:**

- `(?i)`プレフィックスで大文字小文字無視モードを有効化
- 正規表現の事前コンパイルで実行時性能を向上
- エラーハンドリングでユーザーフレンドリーなメッセージを提供

### ファイル処理ロジック

```go
// ファイルが指定されていない場合は標準入力から読み込む
if len(config.Files) == 0 {
    processReader(os.Stdin, "", re, config)
    return
}

// 指定されたファイルを処理
for _, filename := range config.Files {
    if config.Recursive {
        processRecursive(filename, re, config)
    } else {
        processFile(filename, re, config)
    }
}
```

標準的なUnixツールの動作パターンに従い、ファイル指定がなければ標準入力から読み込みます。

## parseFlags関数

```go
func parseFlags() Config {
    var config Config
    
    flag.StringVar(&config.Pattern, "e", "", "検索パターン（正規表現）")
    flag.BoolVar(&config.ShowLine, "n", false, "行番号を表示")
    flag.BoolVar(&config.IgnoreCase, "i", false, "大文字小文字を区別しない")
    flag.BoolVar(&config.Recursive, "r", false, "ディレクトリを再帰的に検索")
    flag.BoolVar(&config.Invert, "v", false, "マッチしない行を表示")
    flag.BoolVar(&config.Count, "c", false, "マッチした行数のみを表示")
    flag.BoolVar(&config.Help, "h", false, "ヘルプを表示")
    
    flag.Parse()
```

### 引数解析ロジック

```go
// パターンが -e で指定されていない場合、最初の引数をパターンとする
if config.Pattern == "" && flag.NArg() > 0 {
    config.Pattern = flag.Arg(0)
    config.Files = flag.Args()[1:]
} else {
    config.Files = flag.Args()
}
```

**柔軟な引数処理:**

- `-e pattern files...` 形式
- `pattern files...` 形式
の両方をサポートし、一般的なgrepの使用パターンに対応

## processFile関数

```go
func processFile(filename string, re *regexp.Regexp, config Config) {
    file, err := os.Open(filename)
    if err != nil {
        fmt.Fprintf(os.Stderr, "エラー: ファイルを開けません '%s': %v\n", filename, err)
        return
    }
    defer file.Close()
    
    processReader(file, filename, re, config)
}
```

**設計のポイント:**

- ファイル処理とReader処理を分離
- `defer`による確実なリソース解放
- エラーは報告するが処理は継続（他のファイルに影響させない）

## processRecursive関数

```go
func processRecursive(path string, re *regexp.Regexp, config Config) {
    err := filepath.Walk(path, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            fmt.Fprintf(os.Stderr, "エラー: パスにアクセスできません '%s': %v\n", path, err)
            return nil
        }
        
        if !info.IsDir() {
            processFile(path, re, config)
        }
        return nil
    })
}
```

**`filepath.Walk`の使用:**

- ディレクトリツリーの再帰的な探索
- エラーが発生してもnilを返して処理継続
- ディレクトリは除外してファイルのみ処理

## processReader関数（コア処理）

```go
func processReader(reader io.Reader, filename string, re *regexp.Regexp, config Config) {
    scanner := bufio.NewScanner(reader)
    lineNum := 0
    matchCount := 0
    
    for scanner.Scan() {
        lineNum++
        line := scanner.Text()
        matches := re.MatchString(line)
        
        if config.Invert {
            matches = !matches
        }
        
        if matches {
            matchCount++
            if !config.Count {
                printMatch(filename, lineNum, line, config)
            }
        }
    }
}
```

### カウントモード処理

```go
if config.Count {
    if filename != "" {
        fmt.Printf("%s:%d\n", filename, matchCount)
    } else {
        fmt.Printf("%d\n", matchCount)
    }
}
```

**効率的な実装:**

- `bufio.Scanner`による行単位読み込み
- メモリ効率を考慮した逐次処理
- 反転検索の論理的な実装
- ファイル名の有無によるフォーマット切り替え

## printMatch関数

```go
func printMatch(filename string, lineNum int, line string, config Config) {
    var output strings.Builder
    
    // ファイル名を表示（複数ファイルまたはファイル名が指定されている場合）
    if filename != "" {
        output.WriteString(filename)
        output.WriteString(":")
    }
    
    // 行番号を表示
    if config.ShowLine {
        output.WriteString(fmt.Sprintf("%d:", lineNum))
    }
    
    output.WriteString(line)
    fmt.Println(output.String())
}
```

**効率的な文字列構築:**

- `strings.Builder`による効率的な文字列結合
- 条件による出力フォーマットの動的変更
- grepの標準的な出力形式に準拠

## 設計上の特徴

### 1. 関数の責任分離

- 各関数が単一の責任を持つ
- テストしやすい構造
- 拡張性の確保

### 2. エラーハンドリング

- エラーは標準エラー出力に日本語で出力
- 一つのエラーが全体処理を停止させない
- 適切な終了コードの設定

### 3. Unix哲学の実践

- 標準入出力の活用
- パイプ処理への対応
- 小さく単純な機能の組み合わせ

### 4. 性能への配慮

- 正規表現の事前コンパイル
- `bufio.Scanner`による効率的な読み込み
- `strings.Builder`による文字列構築

この実装により、標準的なgrepコマンドの機能を網羅しつつ、Go言語らしい構造化されたコードとなっています。

## bufio.Scannerによる行単位処理の詳細解説

regrepのコア処理では、効率的なファイル読み込みのために`bufio.Scanner`を使用しています。この処理について詳しく解説します。

### bufio.Scannerの基本概念

```go
scanner := bufio.NewScanner(reader)
for scanner.Scan() {
    line := scanner.Text()
    // 行の処理
}
```

この3つのメソッドが組み合わされて、効率的な行単位読み込みを実現しています。

### 1. `bufio.NewScanner(reader)`

```go
scanner := bufio.NewScanner(reader)
```

**役割**: `io.Reader`インターフェースを実装するオブジェクトから`Scanner`を作成

**内部動作**:

- デフォルトで行区切り（`\n`）でスキャンするように設定
- 内部バッファ（デフォルト64KB）を初期化
- 分割関数として`bufio.ScanLines`を設定

**メモリ効率**:

- ファイル全体をメモリに読み込まず、必要な分だけバッファリング
- 大きなファイルでもメモリ使用量を抑制

### 2. `scanner.Scan()`

```go
for scanner.Scan() {
    // ループ本体
}
```

**役割**: 次のトークン（行）を読み込み、利用可能かどうかを返す

**戻り値**:

- `true`: 新しいトークンが利用可能
- `false`: EOFに達したかエラーが発生

**内部動作**:

1. バッファから次の行を探索
2. 改行文字（`\n`、`\r\n`）を検出
3. 行データをスキャナ内部に保存
4. 改行文字は除去される

**エラーハンドリング**:

```go
for scanner.Scan() {
    // 処理
}
if err := scanner.Err(); err != nil {
    // エラー処理
}
```

### 3. `scanner.Text()`

```go
line := scanner.Text()
```

**役割**: 最後に成功した`Scan()`呼び出しで読み込まれたテキストを返す

**特徴**:

- 改行文字は含まれない
- `string`型で返される
- `Scan()`が`false`を返した後は空文字列

**メモリ管理**:

- 内部的には`[]byte`で管理
- `Text()`呼び出し時に`string`に変換

### regrepでの実装例

```go
func processReader(reader io.Reader, filename string, re *regexp.Regexp, config Config) {
    scanner := bufio.NewScanner(reader)  // ①Scannerを作成
    lineNum := 0
    matchCount := 0

    for scanner.Scan() {                 // ②行をループで読み込み
        lineNum++
        line := scanner.Text()           // ③現在の行を取得
        matches := re.MatchString(line)  // ④正規表現でマッチング

        if config.Invert {
            matches = !matches
        }

        if matches {
            matchCount++
            if !config.Count {
                printMatch(filename, lineNum, line, config)
            }
        }
    }

    // ⑤エラーチェック
    if err := scanner.Err(); err != nil {
        fmt.Fprintf(os.Stderr, "エラー: 読み込み中にエラーが発生しました: %v\n", err)
    }
}
```

### 他の読み込み方法との比較

#### 1. 一度に全体を読み込む場合

```go
// メモリ効率が悪い
data, err := io.ReadAll(reader)
if err != nil {
    return err
}
lines := strings.Split(string(data), "\n")
for _, line := range lines {
    // 処理
}
```

**問題点**:

- 大きなファイルでメモリ不足の可能性
- ファイル全体を読み終わるまで処理開始できない

#### 2. bufio.Readerを直接使用

```go
reader := bufio.NewReader(file)
for {
    line, err := reader.ReadLine()
    if err == io.EOF {
        break
    }
    if err != nil {
        return err
    }
    // 処理
}
```

**Scanner使用の利点**:

- エラーハンドリングが簡潔
- 長い行の自動処理
- 異なる分割パターンに対応可能

### Scannerの高度な機能

#### カスタム分割関数

```go
// 単語単位で分割
scanner.Split(bufio.ScanWords)

// カスタム分割関数
scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
    // カスタムロジック
    return
})
```

#### バッファサイズ調整

```go
scanner := bufio.NewScanner(reader)
buf := make([]byte, 1024*1024) // 1MBバッファ
scanner.Buffer(buf, 1024*1024)
```

### パフォーマンス特性

**メモリ使用量**: O(行の最大長)
**時間計算量**: O(n) - ファイルサイズに比例
**I/O効率**: バッファリングにより最適化

### 実際のベンチマーク結果

regrepのテストで測定されたパフォーマンス（Apple M1 Max）:

- **ProcessReader**: 930μs/op, 214KB/op, 9002 allocs/op
- 3000行のテストデータを効率的に処理

### エラーハンドリングのベストプラクティス

```go
scanner := bufio.NewScanner(reader)
for scanner.Scan() {
    line := scanner.Text()
    // 行の処理
}

// 重要: ループ終了後のエラーチェック
if err := scanner.Err(); err != nil {
    log.Printf("読み込みエラー: %v", err)
    return err
}
```

この`Scanner`パターンにより、regrepは大きなファイルでも効率的に行単位処理を行えています。Goにおける標準的な行単位ファイル処理のイディオムとして、多くのCLIツールで採用されている手法です。
