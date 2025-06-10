# jsonify - JSON 整形・バリデータ

JSON整形、バリデーション、キーソート、スキーマチェックに対応したCLIツールです。

## 機能

- ✅ JSON整形（インデント調整、見やすい表示）
- ✅ JSONバリデーション（構文チェック）
- ✅ キーのアルファベット順ソート
- ✅ JSONスキーマによるバリデーション

## インストール

```bash
go build -o jsonify .
```

## 使用方法

### JSON整形

```bash
# 標準入力から読み込み、整形して出力
echo '{"name":"John","age":30}' | ./jsonify format

# ファイルから読み込み、整形して出力
./jsonify format -f input.json

# キーをソートして整形
./jsonify format -s -f input.json

# カスタムインデント（タブ）
./jsonify format -i $'\t' -f input.json

# ファイルに出力
./jsonify format -f input.json -o output.json
```

### JSONバリデーション

```bash
# 標準入力からバリデーション
echo '{"name":"John","age":30}' | ./jsonify validate

# ファイルをバリデーション
./jsonify validate -f data.json
```

### スキーマバリデーション

```bash
# スキーマファイルと照合してバリデーション
./jsonify schema -s schema.json -f data.json

# 標準入力とスキーマファイル
echo '{"name":"John","age":30}' | ./jsonify schema -s person-schema.json
```

## オプション

### format コマンド
- `-i, --indent`: インデント文字列（デフォルト: 2スペース）
- `-s, --sort`: キーをアルファベット順にソート
- `-f, --input`: 入力ファイル（デフォルト: 標準入力）
- `-o, --output`: 出力ファイル（デフォルト: 標準出力）

### validate コマンド
- `-f, --input`: 入力ファイル（デフォルト: 標準入力）

### schema コマンド
- `-s, --schema`: スキーマファイル（必須）
- `-f, --input`: 入力ファイル（デフォルト: 標準入力）

## 使用例

### 基本的な整形
```bash
echo '{"z":3,"a":1,"b":2}' | ./jsonify format -s
```

出力:
```json
{
  "a": 1,
  "b": 2,
  "z": 3
}
```

### スキーマバリデーション
person-schema.json:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "number", "minimum": 0}
  },
  "required": ["name", "age"]
}
```

```bash
echo '{"name":"John","age":30}' | ./jsonify schema -s person-schema.json
# ✅ JSON is valid according to the schema
``` 