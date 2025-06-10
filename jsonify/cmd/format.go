package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sort"

	"github.com/spf13/cobra"
)

var (
	indent     string
	sortKeys   bool
	inputFile  string
	outputFile string
)

var formatCmd = &cobra.Command{
	Use:   "format",
	Short: "Format and prettify JSON",
	Long:  `Format JSON with proper indentation and optionally sort keys`,
	RunE:  runFormat,
}

func init() {
	rootCmd.AddCommand(formatCmd)
	formatCmd.Flags().StringVarP(&indent, "indent", "i", "  ", "Indentation string (default: 2 spaces)")
	formatCmd.Flags().BoolVarP(&sortKeys, "sort", "s", false, "Sort keys alphabetically")
	formatCmd.Flags().StringVarP(&inputFile, "input", "f", "", "Input file (default: stdin)")
	formatCmd.Flags().StringVarP(&outputFile, "output", "o", "", "Output file (default: stdout)")
}

func runFormat(cmd *cobra.Command, args []string) error {
	var input io.Reader = os.Stdin
	var output io.Writer = os.Stdout

	// Input source
	if inputFile != "" {
		file, err := os.Open(inputFile)
		if err != nil {
			return fmt.Errorf("failed to open input file: %w", err)
		}
		defer file.Close()
		input = file
	}

	// Output destination
	if outputFile != "" {
		file, err := os.Create(outputFile)
		if err != nil {
			return fmt.Errorf("failed to create output file: %w", err)
		}
		defer file.Close()
		output = file
	}

	// Read JSON
	data, err := io.ReadAll(input)
	if err != nil {
		return fmt.Errorf("failed to read input: %w", err)
	}

	// Parse JSON
	var jsonData interface{}
	if err := json.Unmarshal(data, &jsonData); err != nil {
		return fmt.Errorf("invalid JSON: %w", err)
	}

	// Sort keys if requested
	if sortKeys {
		jsonData = sortJSONKeys(jsonData)
	}

	// Format JSON
	formatted, err := json.MarshalIndent(jsonData, "", indent)
	if err != nil {
		return fmt.Errorf("failed to format JSON: %w", err)
	}

	// Output formatted JSON
	fmt.Fprintln(output, string(formatted))
	return nil
}

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
