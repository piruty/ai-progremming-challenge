package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

type Config struct {
	Pattern    string
	Files      []string
	ShowLine   bool
	IgnoreCase bool
	Recursive  bool
	Invert     bool
	Count      bool
	Help       bool
}

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
}

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

	// パターンが -e で指定されていない場合、最初の引数をパターンとする
	if config.Pattern == "" && flag.NArg() > 0 {
		config.Pattern = flag.Arg(0)
		config.Files = flag.Args()[1:]
	} else {
		config.Files = flag.Args()
	}

	return config
}

func printUsage() {
	fmt.Println("使用方法: regrep [オプション] パターン [ファイル...]")
	fmt.Println()
	fmt.Println("正規表現でファイル内の文字列を検索するgrep風コマンド")
	fmt.Println()
	fmt.Println("オプション:")
	fmt.Println("  -e パターン    検索パターン（正規表現）")
	fmt.Println("  -n            行番号を表示")
	fmt.Println("  -i            大文字小文字を区別しない")
	fmt.Println("  -r            ディレクトリを再帰的に検索")
	fmt.Println("  -v            マッチしない行を表示")
	fmt.Println("  -c            マッチした行数のみを表示")
	fmt.Println("  -h            このヘルプを表示")
	fmt.Println()
	fmt.Println("例:")
	fmt.Println("  regrep \"func.*main\" *.go")
	fmt.Println("  regrep -n -i \"error\" /var/log/app.log")
	fmt.Println("  regrep -r \"TODO\" ./src/")
	fmt.Println("  cat file.txt | regrep \"pattern\"")
}

func processFile(filename string, re *regexp.Regexp, config Config) {
	file, err := os.Open(filename)
	if err != nil {
		fmt.Fprintf(os.Stderr, "エラー: ファイルを開けません '%s': %v\n", filename, err)
		return
	}
	defer file.Close()

	processReader(file, filename, re, config)
}

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

	if err != nil {
		fmt.Fprintf(os.Stderr, "エラー: 再帰検索中にエラーが発生しました: %v\n", err)
	}
}

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

	if config.Count {
		if filename != "" {
			fmt.Printf("%s:%d\n", filename, matchCount)
		} else {
			fmt.Printf("%d\n", matchCount)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "エラー: 読み込み中にエラーが発生しました: %v\n", err)
	}
}

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
