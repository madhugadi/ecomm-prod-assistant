SELECT
    TestValue,
    LEN(TestValue) AS TotalLen,
    (LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '0', '')) 
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '1', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '2', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '3', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '4', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '5', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '6', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '7', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '8', ''))
     + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '9', ''))
    ) AS DigitCount,
    CASE 
        WHEN TestValue NOT LIKE '%[^0-9 .,-]%' THEN 'HARD (no letters at all)'
        WHEN (LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '0', '')) 
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '1', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '2', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '3', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '4', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '5', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '6', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '7', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '8', ''))
             + LEN(TestValue) - LEN(REPLACE(TestValue COLLATE Latin1_General_BIN, '9', ''))
            ) * 2 >= LEN(TestValue) THEN 'HARD (digit-dominant, code-like)'
        ELSE 'SOFT (name with minor issue)'
    END AS Classification
FROM (VALUES
    (N'John2'),           -- expect SOFT (name-dominant)
    (N'TS2993B 1'),       -- expect HARD (digit-dominant, code-like)
    (N'08 0000523 084'),  -- expect HARD (digit-dominant)
    (N'Mary-Jane1'),      -- expect SOFT (name-dominant)
    (N'183'),             -- expect HARD (no letters)
    (N'張'),               -- expect pass-through, not in this test but should not be HARD
    (N'TV727A1')           -- expect HARD (digit-dominant, code-like)
) AS TestData(TestValue);
