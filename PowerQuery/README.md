# Power Query (M) Scripts

This folder contains reusable M language scripts for Power BI's Power Query Editor.

| File | Contents |
|---|---|
| [`common_transformations.pq`](common_transformations.pq) | 10 ready-to-use patterns for loading, cleaning, joining, and shaping data |

## How to Use

1. In Power BI Desktop, open **Power Query Editor** (Home → Transform Data).
2. Select the query you want to modify, or create a new blank query.
3. Click **View → Advanced Editor**.
4. Paste the M snippet, adjust source paths / column names, and click **Done**.

## Patterns Included

| # | Pattern | Description |
|---|---|---|
| 1 | Load CSV | Import a local CSV with proper type casting |
| 2 | Remove duplicates & nulls | Clean out bad rows |
| 3 | Add conditional column | Map values to categories |
| 4 | Unpivot columns | Reshape wide tables to tall/narrow format |
| 5 | Merge (join) queries | Left-outer join two tables on a key |
| 6 | Group and aggregate | Sum and count per category |
| 7 | Dynamic date table | Auto-generating calendar table up to today |
| 8 | Trim & clean text | Normalize casing, spacing, and characters |
| 9 | Filter by date range | Slice rows between two dates |
| 10 | Append multiple tables | Combine yearly Excel files into one dataset |

## Tips

- Always load data through Power Query before adding DAX measures — clean data at the source.
- Use **Close & Apply** (not just Apply) to push changes back to the model.
- Disable query load for staging/intermediate queries to keep the model lean.
- Prefer `Table.TransformColumnTypes` at the end of each query to ensure correct data types.
