import { describe, it, expect } from 'vitest'

// 文字数カウント関数
export const countCharacters = (text: string): number => {
  return text.length
}

// 単語数カウント関数
export const countWords = (text: string): number => {
  return text.trim() ? text.trim().split(/\s+/).length : 0
}

// Markdownの基本要素チェック関数
export const hasMarkdownElements = (text: string): { [key: string]: boolean } => {
  return {
    hasHeaders: /^#{1,6}\s/m.test(text),
    hasLinks: /\[.*?\]\(.*?\)/.test(text),
    hasCodeBlocks: /```/.test(text),
    hasInlineCode: /`[^`]+`/.test(text),
    hasBold: /\*\*.*?\*\*/.test(text),
    hasItalic: /\*.*?\*/.test(text),
    hasLists: /^[-*+]\s/m.test(text) || /^\d+\.\s/m.test(text)
  }
}

describe('Markdown utilities', () => {
  describe('countCharacters', () => {
    it('空の文字列の文字数は0', () => {
      expect(countCharacters('')).toBe(0)
    })

    it('通常の文字列の文字数を正しくカウント', () => {
      expect(countCharacters('Hello')).toBe(5)
      expect(countCharacters('Hello World')).toBe(11)
    })

    it('日本語文字列の文字数を正しくカウント', () => {
      expect(countCharacters('こんにちは')).toBe(5)
      expect(countCharacters('こんにちは世界')).toBe(7)
    })

    it('改行とスペースを含む文字列', () => {
      expect(countCharacters('Hello\nWorld')).toBe(11)
      expect(countCharacters('  Hello  ')).toBe(9)
    })
  })

  describe('countWords', () => {
    it('空の文字列の単語数は0', () => {
      expect(countWords('')).toBe(0)
      expect(countWords('   ')).toBe(0)
    })

    it('単語数を正しくカウント', () => {
      expect(countWords('Hello')).toBe(1)
      expect(countWords('Hello World')).toBe(2)
      expect(countWords('One Two Three Four')).toBe(4)
    })

    it('前後のスペースを無視', () => {
      expect(countWords('  Hello World  ')).toBe(2)
    })

    it('複数のスペースで区切られた単語', () => {
      expect(countWords('Hello    World')).toBe(2)
    })

    it('改行で区切られた単語', () => {
      expect(countWords('Hello\nWorld\nTest')).toBe(3)
    })
  })

  describe('hasMarkdownElements', () => {
    it('見出しを検出', () => {
      const result = hasMarkdownElements('# Title\n## Subtitle')
      expect(result.hasHeaders).toBe(true)
    })

    it('リンクを検出', () => {
      const result = hasMarkdownElements('Click [here](http://example.com)')
      expect(result.hasLinks).toBe(true)
    })

    it('コードブロックを検出', () => {
      const result = hasMarkdownElements('```javascript\ncode\n```')
      expect(result.hasCodeBlocks).toBe(true)
    })

    it('インラインコードを検出', () => {
      const result = hasMarkdownElements('Use `console.log()` for debugging')
      expect(result.hasInlineCode).toBe(true)
    })

    it('太字を検出', () => {
      const result = hasMarkdownElements('This is **bold** text')
      expect(result.hasBold).toBe(true)
    })

    it('斜体を検出', () => {
      const result = hasMarkdownElements('This is *italic* text')
      expect(result.hasItalic).toBe(true)
    })

    it('リストを検出', () => {
      const result1 = hasMarkdownElements('- Item 1\n- Item 2')
      expect(result1.hasLists).toBe(true)

      const result2 = hasMarkdownElements('1. First\n2. Second')
      expect(result2.hasLists).toBe(true)
    })

    it('要素が存在しない場合はfalse', () => {
      const result = hasMarkdownElements('Plain text without markdown')
      expect(result.hasHeaders).toBe(false)
      expect(result.hasLinks).toBe(false)
      expect(result.hasCodeBlocks).toBe(false)
      expect(result.hasInlineCode).toBe(false)
      expect(result.hasBold).toBe(false)
      expect(result.hasItalic).toBe(false)
      expect(result.hasLists).toBe(false)
    })
  })
}) 