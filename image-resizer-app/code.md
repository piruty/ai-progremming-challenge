# 画像リサイズ & 圧縮アプリ - 実装解説

## 📋 プロジェクト概要

このプロジェクトは、ドラッグ&ドロップ対応の画像リサイズ・圧縮GUIアプリケーションです。Python + tkinterを使用し、MVCアーキテクチャパターンを採用して設計されています。

### 🎯 主要機能

- **ドラッグ&ドロップ対応**：画像ファイルを直接ドロップして読み込み
- **柔軟なリサイズ**：幅・高さ指定、比率維持オプション、複数のリサンプリング方法
- **圧縮機能**：JPEG、PNG、WEBP形式での出力、品質調整
- **リアルタイムプレビュー**：設定変更の即座な反映
- **非同期保存**：UIをブロックしない保存処理
- **包括的テスト**：32のテストケースで品質保証

### 🛠️ 技術スタック

- **言語**: Python 3.8+
- **GUI**: tkinter + tkinterdnd2（ドラッグ&ドロップ）
- **画像処理**: Pillow (PIL)
- **パッケージ管理**: uv
- **テスト**: unittest
- **コード品質**: black, isort, flake8, mypy

## 🏗️ アーキテクチャ設計

### MVCパターンの採用

このアプリケーションは、保守性と拡張性を重視してMVCパターンを採用しています：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Model       │    │    Controller   │    │      View       │
│                 │    │                 │    │                 │
│ • 設定管理      │◄──►│ • アプリロジック │◄──►│ • UI表示        │
│ • 画像処理      │    │ • イベント処理   │    │ • ユーザー操作   │
│ • データ構造    │    │ • Model-View連携 │    │ • プレビュー     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### ディレクトリ構造

```
image-resizer-app/
├── models/                    # データモデル層
│   ├── __init__.py
│   ├── settings.py           # 設定管理（@dataclass活用）
│   └── image_processor.py    # 画像処理ロジック
├── views/                     # ビュー層
│   ├── __init__.py
│   └── main_window.py        # メインUI（tkinter）
├── controllers/               # コントローラー層
│   ├── __init__.py
│   └── app_controller.py     # アプリケーションロジック
├── utils/                     # ユーティリティ
│   ├── __init__.py
│   └── file_utils.py         # ファイル操作関数
├── tests/                     # テストスイート
│   ├── __init__.py
│   ├── test_settings.py      # 設定モデルテスト
│   ├── test_image_processor.py # 画像処理テスト
│   └── test_file_utils.py    # ユーティリティテスト
├── main.py                    # エントリーポイント（45行）
├── run_tests.py              # テスト実行スクリプト
├── pyproject.toml            # プロジェクト設定（uv）
├── README.md                 # 使用方法
└── code.md                   # 実装解説（このファイル）
```

## 📁 詳細実装解説

### 1. Models層 - データと設定管理

#### `models/settings.py` - 設定管理

```python
@dataclass
class ResizeSettings:
    """リサイズ設定を管理するデータクラス"""
    width: int = 800
    height: int = 600
    maintain_ratio: bool = True
    method: str = "LANCZOS"
```

**設計のポイント**：
- `@dataclass`により型安全な設定管理
- デフォルト値を明確に定義
- PILライブラリとの連携メソッド提供
- 設定の検証と変換ロジックを内包

**主要クラス**：
- `ResizeSettings`: リサイズパラメータ管理
- `CompressionSettings`: 圧縮・保存設定
- `AppSettings`: アプリケーション全体設定

#### `models/image_processor.py` - 画像処理エンジン

```python
class ImageProcessor:
    """画像処理を行うクラス"""
    
    def resize_image(self, resize_settings: ResizeSettings) -> Image.Image:
        """設定に基づいて画像をリサイズ"""
        # 比率計算 → リサイズ実行 → 結果保存
```

**機能**：
- 画像読み込み・管理
- 比率を考慮したサイズ計算
- 複数リサンプリング方法対応
- プレビュー画像生成
- ファイル保存機能

**エラーハンドリング**：
- 適切な例外メッセージ
- 状態チェック（画像読み込み済みか等）
- リソース管理

### 2. Views層 - ユーザーインターフェース

#### `views/main_window.py` - メインUI

```python
class MainWindow:
    """メインウィンドウのUIクラス"""
    
    def setup_ui(self):
        """UI構築：パネル分割、コントロール配置"""
        # 左側：操作パネル | 右側：プレビュー | 下部：進捗・ボタン
```

**UI設計**：
- **3分割レイアウト**: 設定パネル、プレビューエリア、アクションバー
- **レスポンシブ設計**: ウィンドウサイズ変更に対応
- **直感的操作**: ドラッグ&ドロップ、リアルタイムプレビュー
- **視覚的フィードバック**: 進捗バー、状態表示

**コールバック設計**：
```python
# コントローラーからの関数を受け取る設計
self.on_file_select: Optional[Callable[[str], None]] = None
self.on_preview_update: Optional[Callable[[], None]] = None
```

### 3. Controllers層 - ビジネスロジック

#### `controllers/app_controller.py` - アプリケーション制御

```python
class AppController:
    """アプリケーションのメインコントローラー"""
    
    def handle_file_select(self, file_path: str):
        """ファイル選択時の一連の処理を調整"""
        # 画像読み込み → UI更新 → プレビュー生成 → 状態管理
```

**責務**：
- Model-View間の調整
- ユーザーアクション処理
- 非同期処理管理
- エラーハンドリング

**非同期保存処理**：
```python
def _save_image_async(self, file_path: str):
    """UIをブロックしない非同期保存"""
    threading.Thread(target=save_thread, daemon=True).start()
```

### 4. Utils層 - 汎用機能

#### `utils/file_utils.py` - ファイル操作

**主要機能**：
- 対応画像形式判定
- ドラッグ&ドロップデータ解析
- ファイル名重複回避
- ディレクトリ画像検索

```python
def is_supported_image_file(file_path: str) -> bool:
    """拡張子チェックによる対応形式判定"""
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    return Path(file_path).suffix.lower() in supported_extensions
```

## 🧪 テスト戦略

### テスト構成（32テストケース）

#### `tests/test_settings.py` - 設定モデルテスト（14ケース）

```python
def test_get_pil_resample_method(self):
    """PILリサンプリングメソッド変換のテスト"""
    # 各リサンプリング方法の正確な変換をテスト
    # エラーケース（無効値）のテストも含む
```

**テスト対象**：
- デフォルト値検証
- カスタム値設定
- メソッド変換の正確性
- ファイル拡張子生成
- 保存パラメータ生成

#### `tests/test_image_processor.py` - 画像処理テスト（11ケース）

```python
def test_resize_image(self):
    """実際の画像ファイルを使用したリサイズテスト"""
    # 一時ファイル作成 → リサイズ実行 → 結果検証
```

**テスト手法**：
- 一時ファイル使用（`tempfile`）
- 実画像での動作確認
- エラーケース網羅
- 状態遷移テスト

#### `tests/test_file_utils.py` - ユーティリティテスト（7ケース）

**特色**：
- ファイルシステム操作のテスト
- 異常系の確実な検証
- プラットフォーム互換性考慮

### テスト実行

```bash
# 全テスト実行
python run_tests.py

# 特定モジュールのみ
python run_tests.py test_settings

# uvを使用
uv run python run_tests.py
```

## 🎨 設計思想・工夫点

### 1. 拡張性の確保

**プラグイン的な機能追加**：
- 新しいリサンプリング方法の追加が容易
- 出力形式の追加が`settings.py`の修正のみで可能
- UI要素の追加がコントローラーに影響しない

### 2. 保守性の向上

**単一責任原則**：
- 各クラスが明確な役割を持つ
- 機能変更時の影響範囲が限定的
- テストが書きやすい構造

**依存関係の管理**：
```python
# Viewは直接Modelに依存せず、Controllerを介する
controller = AppController(window, settings)  # 依存注入
```

### 3. ユーザビリティの重視

**エラーハンドリング**：
- 分かりやすいエラーメッセージ
- 例外発生時のアプリケーション継続
- プログレスバーによる処理状況の可視化

**直感的な操作**：
- ドラッグ&ドロップ対応
- リアルタイムプレビュー
- 比率維持の自動計算

### 4. パフォーマンス最適化

**非同期処理**：
- 保存処理のバックグラウンド実行
- UIの応答性維持
- 進捗表示との連携

**メモリ管理**：
- 画像の適切な複製管理
- リソースのクリーンアップ
- プレビューサイズの最適化

## 🚀 使用方法

### 基本的な使用手順

1. **アプリケーション起動**
   ```bash
   uv run python main.py
   ```

2. **画像読み込み**
   - ドラッグ&ドロップ、または「ファイルを選択」ボタン

3. **設定調整**
   - リサイズサイズ指定
   - 比率維持オプション
   - 出力形式・品質設定

4. **プレビュー確認**
   - 「プレビュー更新」ボタンで即座に確認

5. **保存**
   - 「保存」または「名前を付けて保存」

### 対応形式

**入力**: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP  
**出力**: JPEG, PNG, WEBP

## 📈 今後の拡張可能性

### 機能拡張

- **バッチ処理**: 複数ファイルの一括処理
- **フィルター機能**: ぼかし、シャープ、色調補正
- **クロップ機能**: 領域選択による切り抜き
- **ヒストリー機能**: 操作履歴の管理・取り消し

### 技術的改善

- **設定の永続化**: JSON/YAML設定ファイル
- **プラグインシステム**: 機能の動的追加
- **国際化対応**: 多言語サポート
- **テーマシステム**: UI外観のカスタマイズ

## 🔧 開発者向け情報

### コードスタイル

- **Black**: コードフォーマット
- **isort**: import文の並び替え
- **flake8**: 構文チェック
- **mypy**: 型チェック

### 新機能開発の流れ

1. Modelに新しいデータ構造を追加
2. Processorに処理ロジックを実装
3. Viewに必要なUI要素を追加
4. Controllerで連携処理を実装
5. テストケースを作成
6. 動作確認・リファクタリング

この設計により、機能追加や修正が安全かつ効率的に行えます。 