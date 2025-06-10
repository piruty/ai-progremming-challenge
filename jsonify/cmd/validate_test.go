package cmd

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

func TestValidateCommand(t *testing.T) {
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
			name:     "有効なJSON - 配列",
			input:    `[{"name":"John"},{"name":"Jane"}]`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - 文字列",
			input:    `"simple string"`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - 数値",
			input:    `123`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - ブール値",
			input:    `true`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - null",
			input:    `null`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - 空オブジェクト",
			input:    `{}`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - 空配列",
			input:    `[]`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "有効なJSON - 複雑なネスト",
			input:    `{"users":[{"name":"John","details":{"age":30,"active":true}}]}`,
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:    "無効なJSON - 閉じ括弧不足",
			input:   `{"name":"John","age":30`,
			wantErr: true,
		},
		{
			name:    "無効なJSON - カンマ不足",
			input:   `{"name":"John" "age":30}`,
			wantErr: true,
		},
		{
			name:    "無効なJSON - 不正なキー",
			input:   `{name:"John","age":30}`,
			wantErr: true,
		},
		{
			name:    "無効なJSON - 余分なカンマ",
			input:   `{"name":"John","age":30,}`,
			wantErr: true,
		},
		{
			name:    "無効なJSON - 不正なエスケープ",
			input:   `{"name":"John\x","age":30}`,
			wantErr: true,
		},
		{
			name:    "無効なJSON - 空の入力",
			input:   ``,
			wantErr: true,
		},
		{
			name:    "無効なJSON - 単なるテキスト",
			input:   `this is not json`,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
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

			// フラグをリセット
			resetValidateFlags()

			// runValidate関数を直接呼び出し
			err := runValidate(nil, []string{})

			// 出力を読み取り
			wOut.Close()
			var output bytes.Buffer
			output.ReadFrom(rOut)

			// 元に戻す
			os.Stdin = oldStdin
			os.Stdout = oldStdout

			if tt.wantErr {
				if err == nil {
					t.Errorf("エラーが期待されましたが、エラーがありませんでした")
				}
				return
			}

			if err != nil {
				t.Errorf("予期しないエラー: %v", err)
				return
			}

			outputStr := strings.TrimSpace(output.String())
			if outputStr != tt.expected {
				t.Errorf("出力が異なります\n期待値: %s\n実際: %s", tt.expected, outputStr)
			}
		})
	}
}

func resetValidateFlags() {
	inputFile = ""
}

func TestValidateCommandWithFile(t *testing.T) {
	// 一時ファイルを作成
	validJSON := `{"name":"John","age":30}`
	invalidJSON := `{"name":"John","age":30`

	// 有効なJSONファイル
	validFile, err := os.CreateTemp("", "valid_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(validFile.Name())

	if _, err := validFile.WriteString(validJSON); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	validFile.Close()

	// 無効なJSONファイル
	invalidFile, err := os.CreateTemp("", "invalid_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(invalidFile.Name())

	if _, err := invalidFile.WriteString(invalidJSON); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	invalidFile.Close()

	tests := []struct {
		name     string
		filename string
		expected string
		wantErr  bool
	}{
		{
			name:     "有効なJSONファイル",
			filename: validFile.Name(),
			expected: "✅ Valid JSON",
			wantErr:  false,
		},
		{
			name:     "無効なJSONファイル",
			filename: invalidFile.Name(),
			wantErr:  true,
		},
		{
			name:     "存在しないファイル",
			filename: "nonexistent.json",
			wantErr:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 出力の準備
			oldStdout := os.Stdout
			rOut, wOut, _ := os.Pipe()
			os.Stdout = wOut

			// フラグをリセット
			resetValidateFlags()
			inputFile = tt.filename

			// runValidate関数を直接呼び出し
			err := runValidate(nil, []string{})

			// 出力を読み取り
			wOut.Close()
			var output bytes.Buffer
			output.ReadFrom(rOut)

			// 元に戻す
			os.Stdout = oldStdout

			if tt.wantErr {
				if err == nil {
					t.Errorf("エラーが期待されましたが、エラーがありませんでした")
				}
				return
			}

			if err != nil {
				t.Errorf("予期しないエラー: %v", err)
				return
			}

			outputStr := strings.TrimSpace(output.String())
			if outputStr != tt.expected {
				t.Errorf("出力が異なります\n期待値: %s\n実際: %s", tt.expected, outputStr)
			}
		})
	}
}
