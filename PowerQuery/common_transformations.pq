// ============================================================
// Common Power Query (M) Transformations
// Paste each snippet into the Advanced Editor in Power BI
// Desktop (Home → Transform Data → Advanced Editor).
// ============================================================


// ── 1. Load a CSV file ──────────────────────────────────────
let
    Source = Csv.Document(
        File.Contents("C:\Data\sales.csv"),
        [Delimiter = ",", Columns = 10, Encoding = 1252, QuoteStyle = QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes   = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"OrderDate",   type date},
            {"SalesAmount", type number},
            {"Quantity",    Int64.Type},
            {"CustomerID",  type text}
        }
    )
in
    ChangedTypes


// ── 2. Remove duplicates & null rows ────────────────────────
let
    Source         = YourPreviousStep,
    RemovedNulls   = Table.SelectRows(Source, each [CustomerID] <> null and [CustomerID] <> ""),
    RemovedDupes   = Table.Distinct(RemovedNulls, {"OrderID"})
in
    RemovedDupes


// ── 3. Add a conditional column ─────────────────────────────
let
    Source       = YourPreviousStep,
    AddedRegion  = Table.AddColumn(
        Source,
        "Region",
        each if [Country] = "US" then "North America"
             else if [Country] = "UK" then "Europe"
             else if [Country] = "AU" then "Asia Pacific"
             else "Other",
        type text
    )
in
    AddedRegion


// ── 4. Unpivot month columns to rows ────────────────────────
let
    Source     = YourPreviousStep,
    Unpivoted  = Table.UnpivotOtherColumns(
        Source,
        {"ProductID", "ProductName"},   -- columns to keep as-is
        "Month",                         -- new attribute column name
        "Sales"                          -- new value column name
    ),
    ChangedType = Table.TransformColumnTypes(
        Unpivoted,
        {{"Sales", type number}}
    )
in
    ChangedType


// ── 5. Merge (join) two queries ─────────────────────────────
let
    Source = Table.NestedJoin(
        Sales,        "CustomerID",
        Customers,    "CustomerID",
        "CustomerData",
        JoinKind.LeftOuter
    ),
    Expanded = Table.ExpandTableColumn(
        Source,
        "CustomerData",
        {"CustomerName", "Segment", "Country"},
        {"CustomerName", "Segment", "Country"}
    )
in
    Expanded


// ── 6. Group and aggregate ──────────────────────────────────
let
    Source  = YourPreviousStep,
    Grouped = Table.Group(
        Source,
        {"Category", "Region"},     -- group-by columns
        {
            {"TotalSales", each List.Sum([SalesAmount]), type number},
            {"OrderCount", each Table.RowCount(_),       Int64.Type}
        }
    )
in
    Grouped


// ── 7. Dynamic date table ───────────────────────────────────
let
    StartDate  = #date(2020, 1, 1),
    EndDate    = Date.From(DateTime.LocalNow()),
    DateList   = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    DateTable  = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    ChangedType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),

    AddYear    = Table.AddColumn(ChangedType, "Year",        each Date.Year([Date]),            Int64.Type),
    AddMonth   = Table.AddColumn(AddYear,     "Month",       each Date.Month([Date]),           Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth,  "MonthName",   each Date.MonthName([Date]),       type text),
    AddQtr     = Table.AddColumn(AddMonthName,"Quarter",     each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddDay     = Table.AddColumn(AddQtr,      "DayOfWeek",   each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddDayName = Table.AddColumn(AddDay,      "DayName",     each Date.DayOfWeekName([Date]),   type text),
    AddIsWknd  = Table.AddColumn(AddDayName,  "IsWeekend",   each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical),
    AddYearMth = Table.AddColumn(AddIsWknd,   "YearMonth",   each Text.From(Date.Year([Date])) & "-" & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"), type text)
in
    AddYearMth


// ── 8. Trim and clean text columns ─────────────────────────
let
    Source   = YourPreviousStep,
    Cleaned  = Table.TransformColumns(
        Source,
        {
            {"CustomerName", each Text.Proper(Text.Trim(_)), type text},
            {"Email",        each Text.Lower(Text.Trim(_)),  type text},
            {"PhoneNumber",  each Text.Remove(_, {" ", "-", "(", ")"}), type text}
        }
    )
in
    Cleaned


// ── 9. Filter rows by date range ───────────────────────────
let
    Source    = YourPreviousStep,
    StartDate = #date(2023, 1, 1),
    EndDate   = #date(2023, 12, 31),
    Filtered  = Table.SelectRows(
        Source,
        each [OrderDate] >= StartDate and [OrderDate] <= EndDate
    )
in
    Filtered


// ── 10. Append multiple tables ──────────────────────────────
let
    Sales2022   = Excel.Workbook(File.Contents("C:\Data\Sales2022.xlsx"), true){[Item="Sales",Kind="Sheet"]}[Data],
    Sales2023   = Excel.Workbook(File.Contents("C:\Data\Sales2023.xlsx"), true){[Item="Sales",Kind="Sheet"]}[Data],
    Sales2024   = Excel.Workbook(File.Contents("C:\Data\Sales2024.xlsx"), true){[Item="Sales",Kind="Sheet"]}[Data],
    Combined    = Table.Combine({Sales2022, Sales2023, Sales2024})
in
    Combined
