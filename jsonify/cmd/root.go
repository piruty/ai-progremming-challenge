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

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	cobra.OnInitialize()
}
