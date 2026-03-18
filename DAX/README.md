# DAX Formulas

This folder contains ready-to-use DAX code for Power BI.

| File | Contents |
|---|---|
| [`common_measures.dax`](common_measures.dax) | Aggregations, time intelligence, ranking, customer KPIs |
| [`calculated_columns.dax`](calculated_columns.dax) | Calculated columns for dates, revenue bands, profit, segmentation |

## How to Use

### Adding a Measure
1. In Power BI Desktop, go to the **Report** or **Data** view.
2. On the **Home** ribbon, click **New Measure**.
3. Paste the DAX expression into the formula bar and press **Enter**.

### Adding a Calculated Column
1. In Power BI Desktop, go to the **Data** view.
2. Select the target table in the **Fields** pane.
3. On the **Table tools** ribbon, click **New Column**.
4. Paste the DAX expression and press **Enter**.

## Tips

- Use `DIVIDE( numerator, denominator, 0 )` instead of `/` to avoid division-by-zero errors.
- Wrap filter context changes with `CALCULATE()`.
- Mark your date table with **Mark as Date Table** to enable built-in time-intelligence functions.
- Use `VAR … RETURN` to break complex logic into readable steps.
