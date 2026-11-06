# ComfyUI_text_Edit

日本語 | [English](README.md)

ComfyUISAM3DPose からテキスト関連の機能だけを独立させた、ComfyUI 用カスタムノードです。モデルのダウンロードや追加の Python パッケージは不要です。

## インストール

1. 配布 ZIP をダウンロードして展開します。
2. `ComfyUI_text_Edit` フォルダーを `ComfyUI/custom_nodes/` 直下に置きます。`ComfyUI/custom_nodes/ComfyUI_text_Edit/__init__.py` が存在する配置です。
3. ComfyUI を再起動します。ノードは **Text Edit** カテゴリに表示されます。

ZIP をそのまま `custom_nodes` に置いたり、`ComfyUI_text_Edit` フォルダーを二重に入れたりしないでください。

## ノード

| ノード | 機能 |
| --- | --- |
| **Text Input** | 入力した複数行の文字列を出力します。動的プロンプト展開を無効にしているため、括弧なども入力どおりに扱います。 |
| **Text Display** | 実行後、受け取った文字列を読み取り専用欄に表示します。表示内容はワークフローにも保存されます。 |
| **Text Placeholder Replace** | `base_text` 内の `[text1]` ～ `[text16]` を、接続した文字列で置換します。`input_count` で入力端子の表示数を指定します。未接続の箇所はそのまま残り、空文字列を接続した箇所は削除されます。 |
| **JSON Prompt Template** | JSON の値を複数行テンプレートに差し込みます。トップレベルは `{{subject}}`、入れ子や配列は `{{/person/name}}`、`{{/items/0}}` のように参照します。テンプレートが空なら整形済み JSON を出力します。 |

例: `base_text` を `Hello, [text1]!` にして `text1` に `world` を接続すると、出力は `Hello, world!` です。

[workflows/json_to_edit_prompt.json](workflows/json_to_edit_prompt.json) は、`subject`・`outfit`・`composition` の JSON を見出し付き編集プロンプトに変換するサンプルです。ComfyUI に読み込んで使えます。ほかの JSON 形式ではテンプレート内の参照先を変更してください。存在しないキーはパス付きのエラーになります。

JSON 入力はそのままでも、` ```json ` と ` ``` ` で囲まれていても使えます。囲みは解析前に取り除きます。

## 互換性

ノード ID は独立した `TextEditInput`、`TextEditDisplay`、`TextEditPlaceholderReplace`、`TextEditJsonPromptTemplate` です。ComfyUISAM3DPose と同時にインストールできます。元の `SAM3DPoseto...` ノード ID を使った既存ワークフローには、引き続き ComfyUISAM3DPose が必要です。自動置換は行いません。

## 動作確認とライセンス

ComfyUI の Python 環境を使い、このフォルダーで `python -B tests/test_nodes.py` を実行すると、Python 側の機能を確認できます。フロントエンド用スクリプトは `web/js/` にあり、ComfyUI 起動時に読み込まれます。ライセンスは [MIT](LICENSE) です。
