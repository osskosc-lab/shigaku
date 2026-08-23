# Operations

## 毎週の流れ

1. 担当者は週報JSONを作成する。
2. 月曜日の朝礼終了後8:45までに入力検証を完了する。
3. 管理者は圧縮サマリーで、結果差分、前週行動判定、今週行動、責任者、期限、完了状態、検証指標、判断事項だけを確定する。
4. 翌週に同じ検証指標で効果を判定する。

## 実行

```bash
python -m app.main data/weekly/sample_current.json \
  --previous data/weekly/sample_previous.json
```

出力は `data/archive/weekly_meeting_output.json` と `data/archive/manager_view.csv`。欠損がある週報は補完せず停止する。前週週報だけが欠ける場合、当週処理は継続し比較不能を `data_gaps` に残す。

複数行のCSVも入力できる。列名は `results.orders`、`next_action_change.deadline` のようなドット区切りとする。`app.io.export_weekly_csv` でJSONから入力用CSVを生成できる。

## 閾値

初期値は売上達成率80%、訪問化率20%、提案化率30%、見積化率40%。これは運用開始時の警告基準であり、人事評価基準ではない。4週間の基準期間後に実績分布から見直す。
