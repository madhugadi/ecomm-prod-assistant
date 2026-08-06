SELECT
    CASE
        WHEN PERSON_FULL_NAME LIKE '%,%' THEN 'Contains comma'
        WHEN PERSON_FULL_NAME NOT LIKE '% %' THEN 'Single token (no space)'
        WHEN LEN(PERSON_FULL_NAME) - LEN(REPLACE(PERSON_FULL_NAME, ' ', '')) = 1 THEN 'Two tokens (one space)'
        WHEN LEN(PERSON_FULL_NAME) - LEN(REPLACE(PERSON_FULL_NAME, ' ', '')) = 2 THEN 'Three tokens (two spaces)'
        ELSE 'Four+ tokens'
    END AS StructureShape,
    COUNT(*) AS RecordCount
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PERSON_FULL_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FULL_NAME)) <> ''
  AND (PERSON_FIRST_NAME IS NULL OR LTRIM(RTRIM(PERSON_FIRST_NAME)) = '')
  AND (PERSON_LAST_NAME IS NULL OR LTRIM(RTRIM(PERSON_LAST_NAME)) = '')
GROUP BY
    CASE
        WHEN PERSON_FULL_NAME LIKE '%,%' THEN 'Contains comma'
        WHEN PERSON_FULL_NAME NOT LIKE '% %' THEN 'Single token (no space)'
        WHEN LEN(PERSON_FULL_NAME) - LEN(REPLACE(PERSON_FULL_NAME, ' ', '')) = 1 THEN 'Two tokens (one space)'
        WHEN LEN(PERSON_FULL_NAME) - LEN(REPLACE(PERSON_FULL_NAME, ' ', '')) = 2 THEN 'Three tokens (two spaces)'
        ELSE 'Four+ tokens'
    END
ORDER BY RecordCount DESC;
