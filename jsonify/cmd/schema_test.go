package cmd

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

func TestSchemaCommand(t *testing.T) {
	// テスト用のスキーマを作成
	personSchema := `{
		"type": "object",
		"properties": {
			"name": {"type": "string"},
			"age": {"type": "integer", "minimum": 0}
		},
		"required": ["name", "age"]
	}`

	arraySchema := `{
		"type": "array",
		"items": {
			"type": "object",
			"properties": {
				"id": {"type": "integer"},
				"title": {"type": "string"}
			},
			"required": ["id", "title"]
		}
	}`

	// 一時スキーマファイルを作成
	personSchemaFile, err := os.CreateTemp("", "person_schema_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(personSchemaFile.Name())

	if _, err := personSchemaFile.WriteString(personSchema); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	personSchemaFile.Close()

	arraySchemaFile, err := os.CreateTemp("", "array_schema_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(arraySchemaFile.Name())

	if _, err := arraySchemaFile.WriteString(arraySchema); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	arraySchemaFile.Close()

	tests := []struct {
		name       string
		input      string
		schemaFile string
		expected   string
		wantErr    bool
	}{
		{
			name:       "有効なPersonオブジェクト",
			input:      `{"name":"John","age":30}`,
			schemaFile: personSchemaFile.Name(),
			expected:   "✅ JSON is valid according to the schema",
			wantErr:    false,
		},
		{
			name:       "有効な配列",
			input:      `[{"id":1,"title":"Task 1"},{"id":2,"title":"Task 2"}]`,
			schemaFile: arraySchemaFile.Name(),
			expected:   "✅ JSON is valid according to the schema",
			wantErr:    false,
		},
		{
			name:       "空の配列（有効）",
			input:      `[]`,
			schemaFile: arraySchemaFile.Name(),
			expected:   "✅ JSON is valid according to the schema",
			wantErr:    false,
		},
		{
			name:       "必須フィールド不足",
			input:      `{"name":"John"}`,
			schemaFile: personSchemaFile.Name(),
			wantErr:    true,
		},
		{
			name:       "不正な型（文字列→数値）",
			input:      `{"name":"John","age":"thirty"}`,
			schemaFile: personSchemaFile.Name(),
			wantErr:    true,
		},
		{
			name:       "最小値制約違反",
			input:      `{"name":"John","age":-5}`,
			schemaFile: personSchemaFile.Name(),
			wantErr:    true,
		},
		{
			name:       "不正な型（オブジェクト→配列）",
			input:      `{"name":"John","age":30}`,
			schemaFile: arraySchemaFile.Name(),
			wantErr:    true,
		},
		{
			name:       "配列要素の必須フィールド不足",
			input:      `[{"id":1},{"id":2,"title":"Task 2"}]`,
			schemaFile: arraySchemaFile.Name(),
			wantErr:    true,
		},
		{
			name:       "追加プロパティ（許可される）",
			input:      `{"name":"John","age":30,"email":"john@example.com"}`,
			schemaFile: personSchemaFile.Name(),
			expected:   "✅ JSON is valid according to the schema",
			wantErr:    false,
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
			resetSchemaFlags()
			schemaFile = tt.schemaFile

			// runSchema関数を直接呼び出し
			err := runSchema(nil, []string{})

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

func resetSchemaFlags() {
	inputFile = ""
	schemaFile = ""
}

func TestSchemaCommandWithFiles(t *testing.T) {
	// テスト用のスキーマとデータファイルを作成
	schema := `{
		"type": "object",
		"properties": {
			"name": {"type": "string"},
			"age": {"type": "integer", "minimum": 0}
		},
		"required": ["name", "age"]
	}`

	validData := `{"name":"John","age":30}`
	invalidData := `{"name":"John","age":-5}`

	// スキーマファイル
	schemaFileTemp, err := os.CreateTemp("", "schema_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(schemaFileTemp.Name())

	if _, err := schemaFileTemp.WriteString(schema); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	schemaFileTemp.Close()

	// 有効なデータファイル
	validDataFile, err := os.CreateTemp("", "valid_data_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(validDataFile.Name())

	if _, err := validDataFile.WriteString(validData); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	validDataFile.Close()

	// 無効なデータファイル
	invalidDataFile, err := os.CreateTemp("", "invalid_data_*.json")
	if err != nil {
		t.Fatalf("一時ファイルの作成に失敗: %v", err)
	}
	defer os.Remove(invalidDataFile.Name())

	if _, err := invalidDataFile.WriteString(invalidData); err != nil {
		t.Fatalf("ファイルへの書き込みに失敗: %v", err)
	}
	invalidDataFile.Close()

	tests := []struct {
		name       string
		schemaFile string
		dataFile   string
		expected   string
		wantErr    bool
	}{
		{
			name:       "有効なデータファイル",
			schemaFile: schemaFileTemp.Name(),
			dataFile:   validDataFile.Name(),
			expected:   "✅ JSON is valid according to the schema",
			wantErr:    false,
		},
		{
			name:       "無効なデータファイル",
			schemaFile: schemaFileTemp.Name(),
			dataFile:   invalidDataFile.Name(),
			wantErr:    true,
		},
		{
			name:       "存在しないスキーマファイル",
			schemaFile: "nonexistent_schema.json",
			dataFile:   validDataFile.Name(),
			wantErr:    true,
		},
		{
			name:       "存在しないデータファイル",
			schemaFile: schemaFileTemp.Name(),
			dataFile:   "nonexistent_data.json",
			wantErr:    true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 出力の準備
			oldStdout := os.Stdout
			rOut, wOut, _ := os.Pipe()
			os.Stdout = wOut

			// フラグをリセット
			resetSchemaFlags()
			schemaFile = tt.schemaFile
			inputFile = tt.dataFile

			// runSchema関数を直接呼び出し
			err := runSchema(nil, []string{})

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
