SELECT
    TestValue,
    CASE WHEN TestValue NOT LIKE '%[^0-9 .,-]%' 
         THEN 'HARD (no letters of any script)' 
         ELSE 'NOT HARD (has letters - some script)' 
    END AS Classification
FROM (VALUES
    (N'張'),                    -- Chinese, should NOT be Hard
    (N'振华'),                  -- Chinese, should NOT be Hard
    (N'長島'),                  -- Japanese, should NOT be Hard
    (N'キレイコ'),               -- Japanese katakana, should NOT be Hard
    (N'恋'),                    -- Chinese/Japanese, should NOT be Hard
    (N'黄'),                    -- Chinese, should NOT be Hard
    (N'Hübner'),                -- German accented, should NOT be Hard
    (N'Μαγγανά'),               -- Greek, should NOT be Hard
    (N'183'),                   -- pure digits, SHOULD be Hard
    (N'1000645914'),            -- pure digits, SHOULD be Hard
    (N'100005171'),             -- pure digits, SHOULD be Hard
    (N'05 14'),                 -- digits + space, SHOULD be Hard
    (N'TS2993B 1'),             -- has Latin letters mixed in, should NOT be Hard
    (N'.')                      -- just punctuation, SHOULD be Hard
) AS TestData(TestValue);
