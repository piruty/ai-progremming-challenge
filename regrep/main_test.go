package main

import (
	"bytes"
	"os"
	"regexp"
	"strings"
	"testing"
)

// TestConfig tests the Config struct initialization
func TestConfig(t *testing.T) {
	config := Config{
		Pattern:    "test",
		Files:      []string{"file1.txt", "file2.txt"},
		ShowLine:   true,
		IgnoreCase: false,
		Recursive:  true,
		Invert:     false,
		Count:      false,
		Help:       false,
	}

	if config.Pattern != "test" {
		t.Errorf("Expected Pattern to be 'test', got '%s'", config.Pattern)
	}
	if len(config.Files) != 2 {
		t.Errorf("Expected 2 files, got %d", len(config.Files))
	}
	if !config.ShowLine {
		t.Error("Expected ShowLine to be true")
	}
}

// TestProcessReader tests the core processing logic
func TestProcessReader(t *testing.T) {
	tests := []struct {
		name        string
		input       string
		pattern     string
		config      Config
		expected    []string
		expectCount int
	}{
		{
			name:     "Basic pattern match",
			input:    "line1\ntest line\nline3",
			pattern:  "test",
			config:   Config{Pattern: "test"},
			expected: []string{"test line"},
		},
		{
			name:     "Case insensitive match",
			input:    "Line1\nTEST line\nline3",
			pattern:  "test",
			config:   Config{Pattern: "test", IgnoreCase: true},
			expected: []string{"TEST line"},
		},
		{
			name:     "Line numbers",
			input:    "line1\ntest line\nline3",
			pattern:  "test",
			config:   Config{Pattern: "test", ShowLine: true},
			expected: []string{"2:test line"},
		},
		{
			name:     "Invert match",
			input:    "line1\ntest line\nline3",
			pattern:  "test",
			config:   Config{Pattern: "test", Invert: true},
			expected: []string{"line1", "line3"},
		},
		{
			name:        "Count mode",
			input:       "line1\ntest line\nanother test\nline4",
			pattern:     "test",
			config:      Config{Pattern: "test", Count: true},
			expectCount: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Compile regex
			var re *regexp.Regexp
			var err error
			if tt.config.IgnoreCase {
				re, err = regexp.Compile("(?i)" + tt.pattern)
			} else {
				re, err = regexp.Compile(tt.pattern)
			}
			if err != nil {
				t.Fatalf("Failed to compile regex: %v", err)
			}

			// Capture output
			var output bytes.Buffer
			originalStdout := os.Stdout
			r, w, _ := os.Pipe()
			os.Stdout = w

			// Process the input
			reader := strings.NewReader(tt.input)
			processReader(reader, "", re, tt.config)

			// Restore stdout and read output
			w.Close()
			os.Stdout = originalStdout
			output.ReadFrom(r)
			result := strings.TrimSpace(output.String())

			if tt.config.Count {
				// For count mode, check the number
				if !strings.Contains(result, string(rune(tt.expectCount+'0'))) {
					t.Errorf("Expected count %d, got output: %s", tt.expectCount, result)
				}
			} else {
				// For regular output, check expected lines
				lines := strings.Split(result, "\n")
				if len(lines) == 1 && lines[0] == "" {
					lines = []string{}
				}

				if len(lines) != len(tt.expected) {
					t.Errorf("Expected %d lines, got %d. Output: %s", len(tt.expected), len(lines), result)
					return
				}

				for i, expected := range tt.expected {
					if i < len(lines) && !strings.Contains(lines[i], expected) {
						t.Errorf("Expected line %d to contain '%s', got '%s'", i, expected, lines[i])
					}
				}
			}
		})
	}
}

// TestPrintMatch tests the output formatting
func TestPrintMatch(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		lineNum  int
		line     string
		config   Config
		expected string
	}{
		{
			name:     "Basic output",
			filename: "",
			lineNum:  1,
			line:     "test line",
			config:   Config{},
			expected: "test line",
		},
		{
			name:     "With filename",
			filename: "test.txt",
			lineNum:  1,
			line:     "test line",
			config:   Config{},
			expected: "test.txt:test line",
		},
		{
			name:     "With line number",
			filename: "",
			lineNum:  5,
			line:     "test line",
			config:   Config{ShowLine: true},
			expected: "5:test line",
		},
		{
			name:     "With filename and line number",
			filename: "test.txt",
			lineNum:  10,
			line:     "test line",
			config:   Config{ShowLine: true},
			expected: "test.txt:10:test line",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Capture output
			var output bytes.Buffer
			originalStdout := os.Stdout
			r, w, _ := os.Pipe()
			os.Stdout = w

			printMatch(tt.filename, tt.lineNum, tt.line, tt.config)

			w.Close()
			os.Stdout = originalStdout
			output.ReadFrom(r)
			result := strings.TrimSpace(output.String())

			if result != tt.expected {
				t.Errorf("Expected '%s', got '%s'", tt.expected, result)
			}
		})
	}
}

// TestRegexPatterns tests various regex patterns
func TestRegexPatterns(t *testing.T) {
	tests := []struct {
		name    string
		pattern string
		text    string
		match   bool
	}{
		{
			name:    "Simple text match",
			pattern: "hello",
			text:    "hello world",
			match:   true,
		},
		{
			name:    "Regex dot",
			pattern: "h.llo",
			text:    "hello world",
			match:   true,
		},
		{
			name:    "Regex star",
			pattern: "hel*o",
			text:    "helo world",
			match:   true,
		},
		{
			name:    "Regex plus",
			pattern: "hel+o",
			text:    "hello world",
			match:   true,
		},
		{
			name:    "Regex anchors",
			pattern: "^hello",
			text:    "hello world",
			match:   true,
		},
		{
			name:    "Regex anchors no match",
			pattern: "^world",
			text:    "hello world",
			match:   false,
		},
		{
			name:    "Case sensitive",
			pattern: "Hello",
			text:    "hello world",
			match:   false,
		},
		{
			name:    "Character class",
			pattern: "[0-9]+",
			text:    "test123",
			match:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			re, err := regexp.Compile(tt.pattern)
			if err != nil {
				t.Fatalf("Failed to compile regex '%s': %v", tt.pattern, err)
			}

			match := re.MatchString(tt.text)
			if match != tt.match {
				t.Errorf("Pattern '%s' against '%s': expected %v, got %v",
					tt.pattern, tt.text, tt.match, match)
			}
		})
	}
}

// TestCaseInsensitiveRegex tests case-insensitive regex compilation
func TestCaseInsensitiveRegex(t *testing.T) {
	tests := []struct {
		name    string
		pattern string
		text    string
		match   bool
	}{
		{
			name:    "Case insensitive match",
			pattern: "(?i)hello",
			text:    "HELLO world",
			match:   true,
		},
		{
			name:    "Case insensitive no match",
			pattern: "(?i)goodbye",
			text:    "HELLO world",
			match:   false,
		},
		{
			name:    "Mixed case pattern",
			pattern: "(?i)HeLLo",
			text:    "hello world",
			match:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			re, err := regexp.Compile(tt.pattern)
			if err != nil {
				t.Fatalf("Failed to compile regex '%s': %v", tt.pattern, err)
			}

			match := re.MatchString(tt.text)
			if match != tt.match {
				t.Errorf("Pattern '%s' against '%s': expected %v, got %v",
					tt.pattern, tt.text, tt.match, match)
			}
		})
	}
}

// BenchmarkProcessReader benchmarks the core processing function
func BenchmarkProcessReader(t *testing.B) {
	// Create test data
	input := strings.Repeat("test line\nother line\nanother test\n", 1000)
	reader := strings.NewReader(input)
	re, _ := regexp.Compile("test")
	config := Config{Pattern: "test"}

	// Redirect output to discard
	originalStdout := os.Stdout
	os.Stdout, _ = os.Open(os.DevNull)
	defer func() { os.Stdout = originalStdout }()

	t.ResetTimer()
	for i := 0; i < t.N; i++ {
		reader = strings.NewReader(input)
		processReader(reader, "", re, config)
	}
}

// BenchmarkRegexCompile benchmarks regex compilation
func BenchmarkRegexCompile(t *testing.B) {
	pattern := "func.*main"

	t.ResetTimer()
	for i := 0; i < t.N; i++ {
		_, err := regexp.Compile(pattern)
		if err != nil {
			t.Fatal(err)
		}
	}
}

// TestEdgeCases tests edge cases and error conditions
func TestEdgeCases(t *testing.T) {
	t.Run("Empty input", func(t *testing.T) {
		reader := strings.NewReader("")
		re, _ := regexp.Compile("test")
		config := Config{Pattern: "test"}

		// Should not panic
		processReader(reader, "", re, config)
	})

	t.Run("Empty pattern", func(t *testing.T) {
		// This would normally be caught in main(), but test the regex compilation
		_, err := regexp.Compile("")
		if err != nil {
			t.Errorf("Empty pattern should compile successfully, got error: %v", err)
		}
	})

	t.Run("Invalid regex pattern", func(t *testing.T) {
		invalidPatterns := []string{
			"[",
			"*",
			"(?P<invalid",
		}

		for _, pattern := range invalidPatterns {
			_, err := regexp.Compile(pattern)
			if err == nil {
				t.Errorf("Pattern '%s' should have failed to compile", pattern)
			}
		}
	})
}
