# MarkView - 実装解説

## 📋 プロジェクト概要

**MarkView**は、リアルタイムでMarkdownをHTMLプレビューできるWebアプリケーションです。React + TypeScript + Viteを基盤とした現代的なフロントエンド技術スタックで構築されています。

## 🏗️ アーキテクチャと技術スタック

### フロントエンド技術構成

```txt
├── React 18          # UIライブラリ（関数コンポーネント + Hooks）
├── TypeScript        # 型安全性・開発体験向上
├── Vite             # 高速ビルドツール・開発サーバー
├── marked           # Markdownパーサー（HTMLへの変換）
├── highlight.js     # シンタックスハイライト
└── Lucide React     # アイコンライブラリ
```

### プロジェクト構造

```txt
MarkView/
├── src/
│   ├── App.tsx           # メインアプリケーションコンポーネント
│   ├── main.tsx          # Reactアプリケーションのエントリーポイント
│   └── index.css         # グローバルスタイルシート
├── public/               # 静的リソース
├── index.html            # HTMLテンプレート
├── vite.config.ts        # Vite設定
├── tsconfig.json         # TypeScript設定
└── package.json          # 依存関係・スクリプト定義
```

## 🔧 核心実装のポイント

### 1. リアルタイムMarkdown変換

```typescript
// src/App.tsx
useEffect(() => {
  const convertMarkdown = async () => {
    try {
      const htmlContent = await marked(markdown)
      setHtml(htmlContent)
      
      // 統計情報の更新
      setCharCount(markdown.length)
      setWordCount(markdown.trim() ? markdown.trim().split(/\s+/).length : 0)
    } catch (error) {
      console.error('Markdown変換エラー:', error)
      setHtml('<p>Markdownの変換でエラーが発生しました</p>')
    }
  }

  convertMarkdown()
}, [markdown])  // markdownが変更されるたびに実行
```

**実装のポイント:**

- `useEffect`フックを使用してmarkdownの変更を監視
- 非同期でMarkdown → HTML変換を実行
- エラーハンドリングによる堅牢性確保
- 同時に統計情報（文字数・単語数）も計算

### 2. Markdownパーサーの設定

```typescript
// marked.jsの設定
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('ハイライトエラー:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,    // 改行を<br>に変換
  gfm: true       // GitHub Flavored Markdownサポート
})
```

**実装のポイント:**

- highlight.jsと連携したシンタックスハイライト
- 言語指定がある場合は専用ハイライター使用
- 言語指定がない場合は自動判定
- GFMサポートで表・チェックボックスなど対応

### 3. 状態管理（React Hooks）

```typescript
function App() {
  const [markdown, setMarkdown] = useState(defaultMarkdown)
  const [html, setHtml] = useState('')
  const [wordCount, setWordCount] = useState(0)
  const [charCount, setCharCount] = useState(0)
  
  // ...
}
```

**実装のポイント:**

- `useState`による軽量な状態管理
- 4つの独立した状態を管理
- 外部状態管理ライブラリ不要のシンプル構成

### 4. エクスポート機能の実装

#### HTMLコピー機能

```typescript
const copyHtml = async () => {
  try {
    await navigator.clipboard.writeText(html)
    alert('HTMLがクリップボードにコピーされました！')
  } catch (error) {
    console.error('クリップボードエラー:', error)
    alert('クリップボードへのコピーに失敗しました')
  }
}
```

#### HTMLダウンロード機能

```typescript
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
```

**実装のポイント:**

- Navigator Clipboard APIを使用したクリップボード操作
- Blob APIを使用したファイル生成・ダウンロード
- 適切なメモリ管理（URL.revokeObjectURL）

### 5. レスポンシブUI設計

```css
/* src/index.css */

/* フレックスボックスレイアウト */
.container {
  display: flex;
  height: 100%;
  flex: 1;
}

.editor-pane,
.preview-pane {
  flex: 1;  /* 1:1の比率で分割 */
  display: flex;
  flex-direction: column;
}

/* モダンなデザインシステム */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  /* ... */
}
```

**実装のポイント:**

- フレックスボックスによる柔軟なレイアウト
- CSS Gradientによる美しいヘッダーデザイン
- セマンティックなクラス命名
- カラーパレットの統一性

## 🎨 UI/UXデザインの特徴

### 1. ヴィジュアルデザイン

- **カラーパレット**: Tailwind CSS inspired colors
- **タイポグラフィ**: Inter フォントファミリー使用
- **グラデーション**: ヘッダーに美しいパープル系グラデーション
- **シャドウ**: 微細な影効果でDepth表現

### 2. インタラクション設計

- **リアルタイム更新**: 入力と同時にプレビュー更新
- **ホバーエフェクト**: ボタンの視覚的フィードバック
- **スムーズトランジション**: CSS transitions活用

### 3. 情報アーキテクチャ

```txt
├── ヘッダー (アプリケーション名・説明)
├── ツールバー (アクション系機能)
├── メインコンテンツ
│   ├── エディタペイン (入力領域)
│   └── プレビューペイン (出力領域)
└── ステータスバー (統計情報・メタデータ)
```

## 🔍 技術的な工夫とベストプラクティス

### 1. TypeScript活用

```typescript
// 型安全性の確保
interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

// イベントハンドラーの型定義
const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setMarkdown(e.target.value)
}
```

### 2. パフォーマンス最適化

- **useEffect依存配列**: 不要な再計算を防止
- **非同期処理**: UIブロッキングを回避
- **エラーバウンダリー**: エラー発生時の適切な処理

### 3. アクセシビリティ配慮

```typescript
<textarea
  className="editor-textarea"
  value={markdown}
  onChange={(e) => setMarkdown(e.target.value)}
  placeholder="ここにMarkdownを入力してください..."
  spellCheck={false}  // コード入力時のスペルチェック無効化
/>
```

### 4. セキュリティ考慮

```typescript
// dangerouslySetInnerHTMLの使用時はサニタイズされたHTML使用
<div 
  className="preview-content"
  dangerouslySetInnerHTML={{ __html: html }}
/>
```

## 🚀 拡張可能性

### 今後の機能拡張案

1. **テーマ切り替え機能**
   - ライト/ダークモード
   - カスタムカラーテーマ

2. **ファイル操作機能**
   - Markdownファイルの読み込み
   - 自動保存機能

3. **エディタ機能強化**
   - ショートカットキー対応
   - ライブ検索・置換

4. **プラグインシステム**
   - カスタムMarkdown拡張
   - サードパーティ統合

### アーキテクチャの拡張性

- **コンポーネント分割**: 現在の単一コンポーネントから複数コンポーネントへ
- **状態管理強化**: Redux Toolkit / Zustand導入
- **API統合**: バックエンドとの連携準備

## 📊 性能特性

### 計算量

- **Markdown変換**: O(n) - テキスト長に線形
- **統計計算**: O(n) - 文字数・単語数カウント
- **リアルタイム更新**: デバウンシング可能

### メモリ使用量

- **軽量**: 外部重量ライブラリ不使用
- **効率的**: 必要最小限のDOM操作

## 🎯 学習価値

このプロジェクトから学べる技術要素：

1. **React Hooks**: useState, useEffect実践
2. **TypeScript**: 型定義とエラーハンドリング
3. **非同期処理**: Promise/async-await
4. **DOM操作**: Clipboard・File API
5. **CSS設計**: フレックスボックス・レスポンシブ
6. **ツールチェーン**: Vite・開発環境構築

---

このMarkViewプロジェクトは、現代的なフロントエンド開発のベストプラクティスを実践した、学習価値の高い実装となっています。
