# Phase 3 Safety Measurement Specification

Freeze date: 2026-08-09 JST

This file is part of the Phase 3 preregistration package and fixes the safety measurement details that were left generic in the Phase 2 audit.

## 1. Psychological safety instrument

Use the **Japanese version of the Psychological Safety Scale for workers** validated by Ochiai & Otsuka, Industrial Health 2022, 60(5), 436-446, DOI: 10.2486/indhealth.2021-0130.

Frozen administration/scoring rules:

- Use the **five published Japanese items exactly as printed in the article Appendix**; do not paraphrase or substitute items during Phase 3.
- Response scale: 1 to 5.
- Item 5 is reverse-coded.
- Individual score: mean of the five scored items.
- Cluster score: mean of valid individual scores in that management cluster.
- Safety-change SD metric: cluster score at review minus cluster baseline score, divided by the pooled baseline individual-score SD across all eligible clusters before randomization.
- Minimum valid response for an individual score: all 5 items answered. No within-person item imputation.
- Cluster survey result is reported only when at least 3 valid individual responses and at least 50% of eligible cluster members respond; otherwise the cluster safety score is missing and the missingness itself is reviewed.

Administration timing:

- Baseline: end of baseline week 4.
- Intervention: end of weeks 4, 8, and 12.
- A serious-event report can trigger review at any time and does not wait for the next survey.

The validation paper reports acceptable reliability/validity in Japanese workers; the Phase 3 study uses this scale as a safety monitor, not as proof of clinical or psychiatric harm.

## 2. Turnover-intention operational safety item

This is a study-specific operational item, not a validated psychometric scale.

Anonymous item:

「現在、今後3か月以内にこの職場を辞めることを具体的に検討していますか。」

Response options:

- はい
- いいえ
- 回答しない

Frozen scoring:

turnover_intention_rate = number of 'はい' / number of valid yes-or-no responses

'回答しない' is not placed in the denominator and is reported as survey missingness.

Safety trigger: absolute increase of 10 percentage points or more from the cluster's baseline rate. A trigger causes independent review; persistence to the next scheduled review is required for the preregistered safety-compatibility falsification rule unless a serious event independently requires immediate stopping.

## 3. Absenteeism operational safety metric

Frozen definition:

absenteeism_rate = unscheduled_absence_person_days / scheduled_person_days

Planned leave, approved annual leave, scheduled holidays, business travel, and training days are excluded from unscheduled absence. The numerator and denominator definitions may not be changed after randomization.

Safety trigger: absolute increase of 10 percentage points or more from the cluster's 4-week baseline rate.

## 4. Serious safety events

The following are not intervention techniques. They are immediate pause events when reported or observed:

- intimidation or threats
- verbal abuse
- personal attacks
- retaliation for reporting, disagreement, or survey participation
- physical violence
- coercive humiliation

The affected intervention elements are paused, data are preserved, and an independent reviewer decides continue / modify / stop. Business performance cannot override this safety review.

## 5. Confidentiality boundary

- Safety surveys are anonymous to the direct manager.
- Individual safety responses are not used for performance evaluation, compensation, promotion, discipline, or target setting.
- Managers receive only cluster-level summaries that satisfy the minimum response rule.
- Serious-event reporting must have a route that bypasses the direct manager when the manager is the subject of the report.
