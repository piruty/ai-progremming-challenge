# MarkView テスト仕様

## テスト環境

- **Vitest**: 高速なJavaScriptテストフレームワーク
- **React Testing Library**: Reactコンポーネントのテスト
- **Storybook**: コンポーネント開発・ドキュメント

## テストの実行

### 単体テスト（Vitest）

```bash
# テスト実行
npm run test

# テストUI（ブラウザ）
npm run test:ui

# カバレッジ付きテスト
npm run test:coverage
```

### Storybook

```bash
# Storybook起動
npm run storybook

# Storybookビルド
npm run build-storybook
```

## テストファイル構成

```
src/
├── App.test.tsx              # メインアプリケーションのテスト
├── utils/
│   └── markdown.test.ts      # Markdownユーティリティのテスト
├── test/
│   ├── setup.ts              # テストセットアップ
│   └── README.md             # このファイル
└── App.stories.tsx           # Storybookストーリー
```

## テストケース

### App.test.tsx
- UI要素の存在確認
- 基本機能の動作確認
- ユーザーインタラクションのテスト

### markdown.test.ts
- 文字数・単語数カウント機能
- Markdown要素の検出機能
- エッジケースの処理

### App.stories.tsx
- コンポーネントの様々な状態の可視化
- ドキュメント自動生成
- インタラクションテスト

## テスト戦略

1. **単体テスト**: 個別の関数・コンポーネントの動作確認
2. **統合テスト**: コンポーネント間の連携確認
3. **ビジュアルテスト**: Storybookでの見た目・状態確認

## カバレッジ目標

- **文**: 80%以上
- **分岐**: 75%以上
- **関数**: 85%以上
- **行**: 80%以上 