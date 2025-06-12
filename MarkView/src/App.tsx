import { useState, useEffect } from 'react'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { FileText, Eye, Download, Copy, Zap } from 'lucide-react'

// マークダウンのレンダラーを設定
marked.setOptions({
  breaks: true,    // 改行を<br>に変換
  gfm: true       // GitHub Flavored Markdownサポート
})

const defaultMarkdown = `# MarkView へようこそ！

**MarkView** は、リアルタイムでMarkdownをHTMLプレビューできる美しいエディタです。

## 主な機能

- ✨ **リアルタイムプレビュー**: 入力と同時にHTMLが更新されます
- 🎨 **シンタックスハイライト**: コードブロックを美しく表示
- 📱 **レスポンシブデザイン**: どんなデバイスでも快適に使用
- 🚀 **高速処理**: 瞬時にレンダリング

## Markdownの例

### コードブロック

\`\`\`javascript
function hello() {
  console.log("Hello, MarkView!");
}
\`\`\`

### 表

| 機能 | 対応状況 |
|-----|---------|
| 見出し | ✅ |
| リスト | ✅ |
| コード | ✅ |
| 表 | ✅ |

### 引用

> これは引用文です。Markdownで簡単に美しい引用を作成できます。

### リスト

1. **番号付きリスト**
   - ネストしたリスト
   - もう一つの項目
2. 二番目の項目

- 普通のリスト
- チェックボックス: [ ] 未完了
- チェックボックス: [x] 完了

### リンク

[MarkView のドキュメント](https://example.com)

---

**左側でMarkdownを編集して、右側でプレビューを確認してください！**
`

function App() {
  const [markdown, setMarkdown] = useState(defaultMarkdown)
  const [html, setHtml] = useState('')
  const [wordCount, setWordCount] = useState(0)
  const [charCount, setCharCount] = useState(0)

  // Markdownを HTML に変換
  useEffect(() => {
    const convertMarkdown = async () => {
      try {
        const htmlContent = await marked(markdown)
        setHtml(htmlContent)
        
        // 文字数・単語数をカウント
        setCharCount(markdown.length)
        setWordCount(markdown.trim() ? markdown.trim().split(/\s+/).length : 0)
        
        // シンタックスハイライトを適用
        setTimeout(() => {
          document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block as HTMLElement)
          })
        }, 0)
      } catch (error) {
        console.error('Markdown変換エラー:', error)
        setHtml('<p>Markdownの変換でエラーが発生しました</p>')
      }
    }

    convertMarkdown()
  }, [markdown])

  // HTMLをクリップボードにコピー
  const copyHtml = async () => {
    try {
      await navigator.clipboard.writeText(html)
      alert('HTMLがクリップボードにコピーされました！')
    } catch (error) {
      console.error('クリップボードエラー:', error)
      alert('クリップボードへのコピーに失敗しました')
    }
  }

  // HTMLをダウンロード
  const downloadHtml = () => {
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'markview-export.html'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="App">
      {/* ヘッダー */}
      <header className="app-header">
        <Zap size={24} />
        <h1 className="app-title">MarkView</h1>
        <span style={{ marginLeft: 'auto', fontSize: '0.875rem', opacity: 0.9 }}>
          リアルタイム Markdown プレビューエディタ
        </span>
      </header>

      {/* ツールバー */}
      <div className="toolbar">
        <button className="toolbar-button" onClick={copyHtml}>
          <Copy size={16} />
          HTMLをコピー
        </button>
        <button className="toolbar-button" onClick={downloadHtml}>
          <Download size={16} />
          HTMLをダウンロード
        </button>
      </div>

      {/* メインコンテンツ */}
      <div className="container">
        {/* エディタ部分 */}
        <div className="editor-pane">
          <div className="header">
            <FileText size={20} />
            Markdown エディタ
          </div>
          <textarea
            className="editor-textarea"
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            placeholder="ここにMarkdownを入力してください..."
            spellCheck={false}
          />
        </div>

        {/* プレビュー部分 */}
        <div className="preview-pane">
          <div className="header">
            <Eye size={20} />
            プレビュー
          </div>
          <div 
            className="preview-content"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
      </div>

      {/* ステータスバー */}
      <div className="status-bar">
        <div>
          文字数: {charCount.toLocaleString()} | 単語数: {wordCount.toLocaleString()}
        </div>
        <div>
          最終更新: {new Date().toLocaleTimeString('ja-JP')}
        </div>
      </div>
    </div>
  )
}

export default App 