package cmd

import (
	"fmt"
	"io"
	"os"

	"github.com/spf13/cobra"
	"github.com/xeipuuv/gojsonschema"
)

var (
	schemaFile string
)

var schemaCmd = &cobra.Command{
	Use:   "schema",
	Short: "Validate JSON against a schema",
	Long:  `Validate JSON data against a JSON schema`,
	RunE:  runSchema,
}

func init() {
	rootCmd.AddCommand(schemaCmd)
	schemaCmd.Flags().StringVarP(&inputFile, "input", "f", "", "Input JSON file (default: stdin)")
	schemaCmd.Flags().StringVarP(&schemaFile, "schema", "s", "", "JSON schema file (required)")
	schemaCmd.MarkFlagRequired("schema")
}

func runSchema(cmd *cobra.Command, args []string) error {
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

	// Read JSON data
	data, err := io.ReadAll(input)
	if err != nil {
		return fmt.Errorf("failed to read input: %w", err)
	}

	// Read schema
	schemaData, err := os.ReadFile(schemaFile)
	if err != nil {
		return fmt.Errorf("failed to read schema file: %w", err)
	}

	// Create schema loader
	schemaLoader := gojsonschema.NewBytesLoader(schemaData)
	documentLoader := gojsonschema.NewBytesLoader(data)

	// Validate
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
		return fmt.Errorf("schema validation failed")
	}

	return nil
}
