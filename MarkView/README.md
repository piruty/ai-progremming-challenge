# MarkView

**MarkView** は、リアルタイムでMarkdownをHTMLプレビューできる美しいエディタです。

![MarkView Preview](https://via.placeholder.com/800x400/667eea/ffffff?text=MarkView+Preview)

## 🚀 主な機能

- ✨ **リアルタイムプレビュー**: 入力と同時にHTMLが更新されます
- 🎨 **シンタックスハイライト**: コードブロックを美しく表示
- 📱 **レスポンシブデザイン**: どんなデバイスでも快適に使用
- 🚀 **高速処理**: 瞬時にレンダリング
- 📊 **統計情報**: 文字数・単語数をリアルタイム表示
- 📥 **エクスポート機能**: HTMLのコピー・ダウンロード
- 🎯 **GitHub Flavored Markdown対応**: 表、チェックボックスなど

## 🛠️ セットアップ

### 前提条件

- Node.js (v18以上)
- npm または yarn

### インストール

1. **依存関係をインストール**

   ```bash
   cd MarkView
   npm install
   ```

2. **開発サーバーを起動**

   ```bash
   npm run dev
   ```

3. **ブラウザでアクセス**

   http://localhost:3000 でアプリケーションが起動します

### ビルド

本番用にビルドする場合：

```bash
npm run build
```

ビルドされたファイルは `dist/` ディレクトリに出力されます。

## 🎯 使用方法

1. **Markdownを編集**
   - 左側のエディタエリアにMarkdownテキストを入力
   - リアルタイムで右側にプレビューが表示されます

2. **機能を活用**
   - **HTMLをコピー**: 生成されたHTMLをクリップボードにコピー
   - **HTMLをダウンロード**: HTMLファイルとしてダウンロード
   - **統計情報**: 下部のステータスバーで文字数・単語数を確認

3. **対応するMarkdown記法**
   - 見出し（H1-H6）
   - 太字・斜体
   - リスト（番号付き・番号なし）
   - リンク・画像
   - コードブロック（シンタックスハイライト付き）
   - 表
   - 引用
   - 水平線
   - チェックボックス

## 🏗️ 技術スタック

- **React 18** - UIライブラリ
- **TypeScript** - 型安全性
- **Vite** - 高速ビルドツール
- **marked** - Markdownパーサー
- **highlight.js** - シンタックスハイライト
- **Lucide React** - アイコンライブラリ

## 📂 プロジェクト構造

```txt
MarkView/
├── public/             # 静的ファイル
├── src/               # ソースコード
│   ├── App.tsx        # メインアプリケーション
│   ├── main.tsx       # エントリーポイント
│   └── index.css      # グローバルスタイル
├── index.html         # HTMLテンプレート
├── package.json       # 依存関係・スクリプト
├── tsconfig.json      # TypeScript設定
├── vite.config.ts     # Vite設定
└── README.md          # このファイル
```

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します！

## 📄 ライセンス

MIT License

---

**MarkView** で快適なMarkdown編集をお楽しみください！ ✨
