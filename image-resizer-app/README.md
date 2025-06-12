# 画像リサイズ & 圧縮アプリ

ドラッグ&ドロップ対応の画像リサイズ・圧縮GUIアプリケーションです。

## 機能

- **ドラッグ&ドロップ対応**: 画像ファイルを直接ドラッグ&ドロップで読み込み
- **画像リサイズ**: 幅・高さを指定してリサイズ
- **比率維持**: アスペクト比を維持したリサイズ
- **リサイズ方法選択**: LANCZOS、BICUBIC、BILINEAR、NEARESTから選択可能
- **画像圧縮**: JPEG、PNG、WEBP形式での出力
- **品質調整**: JPEG・WEBP形式の品質を10%〜100%で調整
- **リアルタイムプレビュー**: リサイズ後の画像をプレビュー表示
- **進捗表示**: 保存処理の進捗を表示

## 対応画像形式

### 入力対応形式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WEBP (.webp)

### 出力対応形式
- JPEG (.jpg)
- PNG (.png)
- WEBP (.webp)

## インストール

### 必要なソフトウェア
- Python 3.8以上
- uv (高速Pythonパッケージマネージャー)

### uvのインストール
まず、uvをインストールしてください：

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew (macOS):**
```bash
brew install uv
```

**pip経由:**
```bash
pip install uv
```

### プロジェクトの初期化と依存関係のインストール

プロジェクトディレクトリで以下のコマンドを実行：

```bash
# プロジェクトの初期化（仮想環境の作成と依存関係のインストール）
uv sync

# 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows
```

### 開発依存関係のインストール（オプション）
開発ツール（black、isort、flake8、mypy）も使用する場合：

```bash
uv sync --extra dev
```

### 従来のpip方式（非推奨）
uvが利用できない場合の代替手段：
```bash
pip install -r requirements.txt
```

## 使用方法

### 起動

**uvを使用（推奨）:**
```bash
# 仮想環境内で実行
uv run python main.py

# または仮想環境をアクティベートして実行
source .venv/bin/activate  # macOS/Linux
python main.py
```

**従来のpython方式:**
```bash
python main.py
```

### 基本的な使い方

1. **画像の読み込み**
   - ドラッグ&ドロップ: 画像ファイルを画面右側のプレビューエリアにドラッグ&ドロップ
   - ファイル選択: 「ファイルを選択」ボタンをクリックして画像を選択

2. **リサイズ設定**
   - 幅・高さ: 数値を入力して希望のサイズを指定
   - 比率を維持: チェックすると元の画像の縦横比を保持
   - リサイズ方法: 画質や処理速度に応じて選択
     - LANCZOS: 高品質（推奨）
     - BICUBIC: 高品質
     - BILINEAR: 標準品質
     - NEAREST: 低品質・高速

3. **圧縮設定**
   - 出力形式: JPEG、PNG、WEBPから選択
   - 品質: JPEG・WEBP形式の場合、10%〜100%で品質を調整
     - PNG形式の場合は品質設定は無効

4. **プレビュー**
   - 「プレビュー更新」ボタンで設定を反映した画像をプレビュー
   - 設定変更後は自動的にプレビューが更新されます

5. **保存**
   - 保存: 元のファイル名に「_resized」を追加して保存
   - 名前を付けて保存: 任意のファイル名で保存

6. **リセット**
   - 「リセット」ボタンで元の画像に戻す

## 使用例

### 写真をWebサイト用に最適化
1. 大きな写真（例：4000x3000）を読み込み
2. 幅を1200、比率維持をチェック
3. 出力形式をJPEG、品質80%に設定
4. プレビューで確認後、保存

### アイコン用画像の作成
1. 元画像を読み込み
2. 幅・高さを128x128に設定（比率維持のチェックを外す）
3. 出力形式をPNGに設定
4. 保存

## uvを使用する利点

- **高速**: pipの10-100倍高速な依存関係解決とインストール
- **信頼性**: 一貫性のある依存関係解決
- **使いやすさ**: 自動的な仮想環境管理
- **現代的**: 最新のPythonパッケージング標準に準拠

## 開発

### Makefileの使用（推奨）

このプロジェクトには開発作業を効率化するMakefileが含まれています：

```bash
# ヘルプを表示
make help

# プロジェクトの初期セットアップ
make install

# アプリケーションを実行
make run

# 全テストを実行
make test

# 個別テスト実行
make test-settings      # 設定モデルのテスト
make test-image        # 画像処理のテスト  
make test-file         # ファイルユーティリティのテスト

# コード品質チェック
make lint              # flake8によるコード品質チェック
make format            # black + isortによるコードフォーマット
make type-check        # mypyによる型チェック
make quality           # 全品質チェック（lint + format + type-check）

# プロジェクト統計
make stats             # ファイル数、行数などの統計情報

# クリーンアップ
make clean             # 一時ファイルの削除

# リリース前チェック
make pre-commit        # 全品質チェック + テスト実行
```

### 手動でのコマンド実行

Makefileを使用しない場合の従来の方法：

```bash
# コードフォーマット
uv run black .
uv run isort .

# リンタ
uv run flake8 .

# 型チェック
uv run mypy .

# テスト実行
uv run python run_tests.py
```

### プロジェクト構造の理解

プロジェクトの詳細な実装解説は `code.md` を参照してください：

- **MVCアーキテクチャの設計思想**
- **各ファイルの責務と実装詳細**
- **テスト戦略と32のテストケース**
- **設計パターンと拡張可能性**
- **今後の機能拡張方針**

```bash
# 実装解説ドキュメントを確認
/bin/cat code.md
```

## 技術仕様

- **開発言語**: Python 3.8+
- **パッケージマネージャー**: uv
- **GUIフレームワーク**: tkinter
- **画像処理**: Pillow (PIL)
- **ドラッグ&ドロップ**: tkinterdnd2
- **マルチスレッド**: threading (保存処理の非同期実行)

## トラブルシューティング

### 起動時のエラー
- `ModuleNotFoundError`: 依存関係がインストールされていません
  ```bash
  uv sync
  ```

### uvが見つからない場合
- uvが正しくインストールされているか確認
- パスが通っているか確認
- 従来のpip方式を使用してください

### ドラッグ&ドロップが動作しない
- tkinterdnd2パッケージが正常にインストールされているか確認
- OSによってはドラッグ&ドロップの動作が制限される場合があります

### 画像が読み込めない
- 対応している画像形式か確認
- ファイルが破損していないか確認
- ファイルのアクセス権限を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 