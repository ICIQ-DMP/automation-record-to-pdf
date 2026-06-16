---
name: Project architecture
description: module layout, CSV format, PDF colour scheme, output naming, field mapping
type: project
---

# automation-record-to-pdf — Architecture

## Module layout

```
main.py                          # CLI entry point (--id, --row, --all)
src/
  models/automation_record.py    # AutomationRecord dataclass
  transformers/ms_list_transformer.py  # CSV row → AutomationRecord
  renderers/pdf_renderer.py      # AutomationRecord → styled A4 PDF
  data_sources/csv_source.py     # CSV file reader
  utils/html_utils.py            # HTML → plain text
input/Template Automatització.csv  # MS List CSV export
output/                          # generated PDFs
```

## CSV columns (current MS List export)

| CSV column | AutomationRecord field | Section |
|---|---|---|
| Nom del procés a automatitzar | process_name | 1 |
| Nom de l´automatització | automation_name | 1 |
| ID intern | internal_id | 1 |
| Version | version | 1 |
| Repositori | repository | 1 |
| Data última actualització | last_update_date | 1 |
| Descripció del procés actual | current_process_description | 1 |
| Descripció del procés automatitzat | automated_process_description | 2 |
| Propietari de l'automatització (product owner) | product_owner | 3 |
| Propietari del procés de negoci (process owner) | process_owner | 3 |
| Arquitecte de software (software arquitect) | software_architect | 3 |
| Manager (responsible) | manager | 3 |
| Desenvolupadors (developers) | developers | 3 |
| Unitats i persones usuàries del procés de negoci | user_units | 3 |
| Persones i/o unitats que reben l'output | output_receivers | 3 |
| Persones i/o unitats que alimenten l'input | input_feeders | 3 |
| Tipus d´automatització | automation_type | 4 |
| Llenguatge i tecnologia | technology | 4 |
| Fonts de dades | data_sources | 4 |
| Output esperat | expected_output | 4 |
| Freqüència execució | execution_frequency | 4 |
| Dependències, credencials i permisos | dependencies_credentials | 4 |
| Beneficis | benefits | 5 |
| Estat actual | current_status | 6 |
| Temps estimat desenvolupament (hores totals) | estimated_dev_time | 6 |
| Data final prevista implementació | implementation_deadline | 6 |
| Millores Futures | future_improvements | 6 |
| Riscos | risks | 7 |

## Removed fields (no longer in CSV)
- creation_date (Data de creació)
- change_reason (Motiu del canvi)
- time_saved (Temps estalviat) — also removed per user request
- economic_impact (Impacte econòmic estimat) — also removed per user request
- actual_dev_time (Temps real invertit) — also removed per user request
- credentials_permissions (Credencials i permisos — now merged into dependencies_credentials)
- data_protection (Protecció de dades)
- logs_traceability (Logs i traçabilitat)

## PDF sections
1. Identificació (7 rows)
2. Context (1 row)
3. Responsabilitats (8 rows, includes output_receivers and input_feeders)
4. Detalls Tècnics (6 rows, combined dependencies_credentials)
5. Beneficis (1 row)
6. Estat i Roadmap (4 rows)
7. Seguretat i Compliance (1 row — only risks)
8. Signatures i Validació — 7 signers in 4-column layout (2 rows of 4)

## Signature signers (all except developers)
Row 1: Unitats i persones usuàries | Propietari de l'automatització | Propietari del procés de negoci | Arquitecte de software
Row 2: Persones que reben l'output | Persones que alimenten l'input | Manager | (empty)

## PDF colour scheme
- Dark navy  #1F3864 — section headers
- Medium blue #2E5FA3 — subtitle
- Light blue  #D6E4F7 — label cells
- Light grey  #F5F7FA — alternating value rows
- Border      #BCC8D8

## Output naming
`fitxa_{id:02d}_{automation_name_slug}.pdf`
