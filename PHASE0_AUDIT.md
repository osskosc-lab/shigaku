# Phase 0 Repository Audit

実施日: 2026-08-23 / 基準コミット: `76fd114d37e7bc157bb2525735a2f87079f16ef0`

## 既存機能

- `run_experiment.py`: P0〜P5を500シードで比較する合成Monte Carlo実験。
- `README.md`: P4_週報最適化が総合効用1位であることと、実績因果効果ではない注意を記載。
- `requirements.txt`: NumPy 2.0以上、pandas 2.2以上。
- `.github/workflows/sales-management-experiment.yml`: 既存実験をPython 3.12で実行し成果物を保存。

## 回帰確認

Python 3.12.13で `python run_experiment.py` を完走。P4_週報最適化の `utility_mean=2.196025`、rank=1を確認した。既存ファイルを移動せず、そのまま保持する。

## 保持対象

既存READMEの研究結論、ルートの `run_experiment.py`、P0〜P5、P4仮説、既存GitHub Actions。合成結果を実績として表示しない。

## 改修対象・追加対象

実運用層として `app/`、`agents/`、`schemas/`、`data/`、`tests/` を追加。研究接続は `research/operational_metrics.py` に限定し、データ出所ラベルを必須化する。

## 技術的リスクと対策

| リスク | 対策 |
|---|---|
| 分母0 | 転換率を `null` とし、0を捏造しない |
| 欠損補完 | `data_gaps` に残し、必須欠損では処理停止 |
| 前週比較不能 | 当週処理は継続し、効果判定を `unknown` とする |
| 自由文の過剰解釈 | 数値前後差がなければ原則 `unknown` |
| 人格・感情評価 | 契約とエージェント文書で禁止 |
| 過剰管理 | 条件付き専門処理と圧縮会議出力を採用 |
| 合成・実績混同 | 保存先と `data_source` を分離 |
| 既存研究破壊 | 研究回帰テストとCIで検査 |

