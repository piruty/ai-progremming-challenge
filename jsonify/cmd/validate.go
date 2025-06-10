package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/spf13/cobra"
)

var validateCmd = &cobra.Command{
	Use:   "validate",
	Short: "Validate JSON syntax",
	Long:  `Validate JSON syntax and report any errors`,
	RunE:  runValidate,
}

func init() {
	rootCmd.AddCommand(validateCmd)
	validateCmd.Flags().StringVarP(&inputFile, "input", "f", "", "Input file (default: stdin)")
}

func runValidate(cmd *cobra.Command, args []string) error {
	var input io.Reader = os.Stdin

	// Input source
	if inputFile != "" {
		file, err := os.Open(inputFile)
		if err != nil {
			return fmt.Errorf("failed to open input file: %w", err)
		}
		defer file.Close()
		input = file
	}

	// Read JSON
	data, err := io.ReadAll(input)
	if err != nil {
		return fmt.Errorf("failed to read input: %w", err)
	}

	// Validate JSON
	var jsonData interface{}
	if err := json.Unmarshal(data, &jsonData); err != nil {
		fmt.Printf("❌ Invalid JSON: %v\n", err)
		return err
	}

	fmt.Println("✅ Valid JSON")
	return nil
}
