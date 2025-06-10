package cmd

import (
	"bytes"
	"strings"
	"testing"

	"github.com/spf13/cobra"
)

func TestRootCommand(t *testing.T) {
	tests := []struct {
		name     string
		args     []string
		expected []string
		wantErr  bool
	}{
		{
			name: "ヘルプ表示",
			args: []string{"--help"},
			expected: []string{
				"jsonify is a CLI tool that provides:",
				"JSON formatting and pretty printing",
				"JSON validation",
				"Key sorting",
				"JSON schema validation",
				"Available Commands:",
				"format",
				"validate",
				"schema",
			},
			wantErr: false,
		},
		{
			name: "短縮ヘルプ",
			args: []string{"-h"},
			expected: []string{
				"jsonify is a CLI tool that provides:",
				"Available Commands:",
			},
			wantErr: false,
		},
		{
			name:    "引数なし（デフォルト動作）",
			args:    []string{},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 新しいコマンドインスタンスを作成
			cmd := &cobra.Command{
				Use:   "jsonify",
				Short: "JSON formatter and validator with schema support",
				Long: `jsonify is a CLI tool that provides:
- JSON formatting and pretty printing
- JSON validation
- Key sorting
- JSON schema validation`,
			}

			// サブコマンドを追加
			cmd.AddCommand(formatCmd)
			cmd.AddCommand(validateCmd)
			cmd.AddCommand(schemaCmd)

			// 出力の準備
			var buf bytes.Buffer
			cmd.SetOut(&buf)
			cmd.SetErr(&buf)

			// コマンド実行
			cmd.SetArgs(tt.args)
			err := cmd.Execute()

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

			output := buf.String()

			// 期待される文字列がすべて出力に含まれているかチェック
			for _, expected := range tt.expected {
				if !strings.Contains(output, expected) {
					t.Errorf("期待される文字列が出力に含まれていません\n期待: %s\n出力: %s", expected, output)
				}
			}
		})
	}
}

func TestExecute(t *testing.T) {
	// Execute関数が正常に動作するかテスト
	// この関数は実際にはrootCmdを実行するラッパーなので、
	// パニックしないことを確認する

	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Execute()でパニックが発生しました: %v", r)
		}
	}()

	// 元のrootCmdを保存
	originalRootCmd := rootCmd

	// テスト用のrootCmdを作成（ヘルプコマンドで即座に終了）
	testRootCmd := &cobra.Command{
		Use:   "jsonify",
		Short: "test",
		Run: func(cmd *cobra.Command, args []string) {
			// 何もしない
		},
	}

	// テスト中はtestRootCmdを使用
	rootCmd = testRootCmd

	// Execute関数をテスト
	err := Execute()

	// 元に戻す
	rootCmd = originalRootCmd

	// エラーが発生しないことを確認
	if err != nil {
		t.Errorf("Execute()でエラーが発生しました: %v", err)
	}
}
