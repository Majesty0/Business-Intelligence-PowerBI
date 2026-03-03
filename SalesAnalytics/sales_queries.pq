// ============================================================
// Sales Analytics — Power Query Setup
// Three queries that build the star schema for the
// SalesAnalytics DAX measures.
// ============================================================


// ── Query 1: Sales (Fact Table) ──────────────────────────────
let
    Source = Csv.Document(
        File.Contents("C:\Data\sales_raw.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Cast column types
    TypedTable = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"OrderID",     type text},
            {"OrderDate",   type date},
            {"CustomerID",  type text},
            {"ProductID",   type text},
            {"SalesAmount", type number},
            {"Quantity",    Int64.Type},
            {"UnitCost",    type number},
            {"Discount",    type number}
        }
    ),

    // Remove rows with missing key fields
    Cleaned = Table.SelectRows(
        TypedTable,
        each [OrderID] <> null and [SalesAmount] <> null and [SalesAmount] >= 0
    ),

    // Ensure Discount is between 0 and 1
    NormalizedDiscount = Table.TransformColumns(
        Cleaned,
        {"Discount", each if _ > 1 then _ / 100 else _, type number}
    )
in
    NormalizedDiscount


// ── Query 2: Customers (Dimension) ───────────────────────────
let
    Source = Excel.Workbook(
        File.Contents("C:\Data\customers.xlsx"),
        true
    ){[Item = "Customers", Kind = "Sheet"]}[Data],

    TypedTable = Table.TransformColumnTypes(
        Source,
        {
            {"CustomerID",   type text},
            {"CustomerName", type text},
            {"Segment",      type text},
            {"Country",      type text},
            {"Region",       type text}
        }
    ),

    // Trim and normalise text
    Cleaned = Table.TransformColumns(
        TypedTable,
        {
            {"CustomerName", each Text.Proper(Text.Trim(_)), type text},
            {"Segment",      each Text.Proper(Text.Trim(_)), type text},
            {"Country",      each Text.Proper(Text.Trim(_)), type text},
            {"Region",       each Text.Upper(Text.Trim(_)),  type text}
        }
    ),

    Deduped = Table.Distinct(Cleaned, {"CustomerID"})
in
    Deduped


// ── Query 3: Products (Dimension) ────────────────────────────
let
    Source = Excel.Workbook(
        File.Contents("C:\Data\products.xlsx"),
        true
    ){[Item = "Products", Kind = "Sheet"]}[Data],

    TypedTable = Table.TransformColumnTypes(
        Source,
        {
            {"ProductID",   type text},
            {"ProductName", type text},
            {"Category",    type text},
            {"SubCategory", type text},
            {"UnitPrice",   type number}
        }
    ),

    Cleaned = Table.TransformColumns(
        TypedTable,
        {
            {"ProductName", each Text.Proper(Text.Trim(_)), type text},
            {"Category",    each Text.Proper(Text.Trim(_)), type text},
            {"SubCategory", each Text.Proper(Text.Trim(_)), type text}
        }
    ),

    Deduped = Table.Distinct(Cleaned, {"ProductID"})
in
    Deduped
