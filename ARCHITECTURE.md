# Architecture

研究層と実運用層を分離する。

```text
JSON weekly report
  -> Report Validator
  -> Pipeline Analyst + Action Change Auditor
  -> Decision Router
  -> conditional specialists
  -> Weekly Report Manager
  -> meeting JSON / manager CSV
```

`run_experiment.py` は既存の合成Monte Carlo研究であり、実績データではない。`research/operational_metrics.py` は実運用データを `data_source=operational` として変換し、欠測を保持する。合成出力は `results/`、実運用入力は `data/weekly/`、処理出力は `data/archive/` に分ける。

エージェントはLLMへの依存を必須とせず、同じ入力と基準時刻に対し再現可能なルールとして実装した。各出力は `schemas/agent_result.schema.json` の共通契約を持つ。

