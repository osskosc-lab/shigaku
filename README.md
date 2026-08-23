# 識学システム / Marukane Sales Weekly Agency

既存の営業部行動管理シミュレーションを保持しつつ、株式会社マルカネ営業部の週報を、結果差分と翌週の行動変化へ接続する実運用システムへ拡張しています。

## 実運用機能

- 週報JSONの必須項目、型、責任者、期限、完了状態、検証指標を検証
- 売上達成率、新規・休眠アプローチ、訪問、提案、見積、転換率を安全に計算
- 前週行動を `effective / ineffective / unknown / not_executed` で判定
- 上司判断、期限超過、接触不足、転換率低下を抽出
- 条件を満たす時だけ専門エージェントへ経路設定
- 毎週月曜日、朝礼終了後8:45会議用の圧縮JSONを生成
- 複数社員の管理者CSVとHTMLダッシュボードを生成
- JSONまたはドット区切り列のCSVで週報を入力
- 合成研究と実運用データを明示的に分離

### 週報処理

```bash
python -m app.main data/weekly/sample_current.json \
  --previous data/weekly/sample_previous.json
```

既定出力は `data/archive/weekly_meeting_output.json`、`manager_view.csv`、`manager_dashboard.html` です。

### テスト

```bash
python -m unittest discover -s tests -v
```

24テストで、正常入力、0除算、期限・責任者欠損、前週比較不能、行動判定、異常値、決定経路、再現性、既存研究回帰を確認します。

設計は [ARCHITECTURE.md](ARCHITECTURE.md)、週次運用は [OPERATIONS.md](OPERATIONS.md) を参照してください。

## 既存研究（保持）

営業部の週報・結果管理を、6つの管理プロトコルで比較する合成Monte Carlo実験です。

### 最終結果

500シード平均では、`P4_週報最適化` が総合効用1位でした。

P4は次を組み合わせます。

- 結果を「期限時の状態」で定義する
- 一つの結果につき責任者を一人にする
- 責任と権限を一致させる
- 週報を「事実 -> 課題 -> 次の行動変化」で記入する
- 翌週に行動変化の効果を数字で検証する
- 確認頻度・入力項目・圧力を増やしすぎない

### 注意

この結果は実績データから推定した因果効果ではありません。識学資料と営業部週報項目を操作変数へ翻訳し、構造仮説を比較した合成シミュレーションです。実運用への採否は、4週間の基準期間と8週間の導入期間で実測してください。

### 実行

```bash
python -m pip install -r requirements.txt
python run_experiment.py
```

出力は `results/` に保存されます。
