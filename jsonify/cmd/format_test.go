package cmd

import (
	"bytes"
	"encoding/json"
	"os"
	"strings"
	"testing"
)

func TestFormatCommand(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		args    []string
		wantErr bool
	}{
		{
			name:    "基本的なJSON整形",
			input:   `{"name":"John","age":30}`,
			args:    []string{},
			wantErr: false,
		},
		{
			name:    "キーソート付き整形",
			input:   `{"z":3,"a":1,"b":2}`,
			args:    []string{"--sort"},
			wantErr: false,
		},
		{
			name:    "カスタムインデント",
			input:   `{"name":"John","age":30}`,
			args:    []string{"--indent", "\t"},
			wantErr: false,
		},
		{
			name:    "ネストしたオブジェクトのキーソート",
			input:   `{"z":{"c":3,"a":1},"a":1}`,
			args:    []string{"--sort"},
			wantErr: false,
		},
		{
			name:    "無効なJSON",
			input:   `{"name":"John","age":30`,
			args:    []string{},
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

			// runFormat関数を直接呼び出し
			resetFormatFlags()

			// フラグを設定
			for i := 0; i < len(tt.args); i += 2 {
				if i+1 < len(tt.args) {
					switch tt.args[i] {
					case "--sort":
						sortKeys = true
						i-- // 値がないフラグの場合
					case "--indent":
						if i+1 < len(tt.args) {
							indent = tt.args[i+1]
						}
					}
				}
			}

			err := runFormat(nil, []string{})

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
			if outputStr == "" {
				t.Errorf("出力が空です")
			}

			// JSONとして有効かチェック
			if !isValidJSON(outputStr) {
				t.Errorf("出力が有効なJSONではありません: %s", outputStr)
			}

			// ソートが指定されている場合、キーがソートされているかチェック
			if sortKeys && tt.input == `{"z":3,"a":1,"b":2}` {
				if !strings.Contains(outputStr, `"a": 1`) ||
					!strings.Contains(outputStr, `"b": 2`) ||
					!strings.Contains(outputStr, `"z": 3`) {
					t.Errorf("キーがソートされていません: %s", outputStr)
				}
				// aがzより前に来ているかチェック
				aIndex := strings.Index(outputStr, `"a"`)
				zIndex := strings.Index(outputStr, `"z"`)
				if aIndex > zIndex {
					t.Errorf("キーがアルファベット順にソートされていません: %s", outputStr)
				}
			}
		})
	}
}

func resetFormatFlags() {
	indent = "  "
	sortKeys = false
	inputFile = ""
	outputFile = ""
}

func isValidJSON(s string) bool {
	var js interface{}
	return json.Unmarshal([]byte(s), &js) == nil
}

func TestSortJSONKeys(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		expected interface{}
	}{
		{
			name: "オブジェクトのキーソート",
			input: map[string]interface{}{
				"z": 3,
				"a": 1,
				"b": 2,
			},
			expected: map[string]interface{}{
				"a": 1,
				"b": 2,
				"z": 3,
			},
		},
		{
			name: "配列の処理",
			input: []interface{}{
				map[string]interface{}{"z": 1, "a": 2},
				"string",
				123,
			},
			expected: []interface{}{
				map[string]interface{}{"a": 2, "z": 1},
				"string",
				123,
			},
		},
		{
			name:     "プリミティブ値",
			input:    "string",
			expected: "string",
		},
		{
			name:     "数値",
			input:    123,
			expected: 123,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := sortJSONKeys(tt.input)

			// 結果の型チェック
			switch expected := tt.expected.(type) {
			case map[string]interface{}:
				resultMap, ok := result.(map[string]interface{})
				if !ok {
					t.Errorf("結果がmap[string]interface{}ではありません")
					return
				}

				for key, value := range expected {
					if resultMap[key] != value {
						t.Errorf("キー %s の値が異なります: 期待値 %v, 実際 %v", key, value, resultMap[key])
					}
				}
			case []interface{}:
				resultSlice, ok := result.([]interface{})
				if !ok {
					t.Errorf("結果が[]interface{}ではありません")
					return
				}

				if len(resultSlice) != len(expected) {
					t.Errorf("配列の長さが異なります: 期待値 %d, 実際 %d", len(expected), len(resultSlice))
					return
				}

				for i, expectedItem := range expected {
					if expectedMap, ok := expectedItem.(map[string]interface{}); ok {
						resultMap, ok := resultSlice[i].(map[string]interface{})
						if !ok {
							t.Errorf("インデックス %d の要素がmap[string]interface{}ではありません", i)
							continue
						}
						for key, value := range expectedMap {
							if resultMap[key] != value {
								t.Errorf("インデックス %d のキー %s の値が異なります", i, key)
							}
						}
					} else if resultSlice[i] != expectedItem {
						t.Errorf("インデックス %d の値が異なります: 期待値 %v, 実際 %v", i, expectedItem, resultSlice[i])
					}
				}
			default:
				if result != tt.expected {
					t.Errorf("結果が異なります: 期待値 %v, 実際 %v", tt.expected, result)
				}
			}
		})
	}
}
