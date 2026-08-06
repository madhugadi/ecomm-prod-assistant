-- How many records actually match the exact pattern Melissa described
-- (First populated, Middle populated, Last is digit-only or digit-dominant)
SELECT COUNT(*) AS MatchingRecords
FROM dbo.Bronze_PII_Table_Consolidated
WHERE UPPER(RECORD_TYPE) = 'PERSON'
  AND PERSON_FIRST_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FIRST_NAME)) <> ''
  AND PERSON_MIDDLE_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_MIDDLE_NAME)) <> ''
  AND PERSON_LAST_NAME IS NOT NULL
  AND PERSON_LAST_NAME NOT LIKE '%[^0-9 ]%';  -- last name is only digits/spaces

-- Sample rows to eyeball
SELECT TOP 30 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME
FROM dbo.Bronze_PII_Table_Consolidated
WHERE UPPER(RECORD_TYPE) = 'PERSON'
  AND PERSON_FIRST_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FIRST_NAME)) <> ''
  AND PERSON_MIDDLE_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_MIDDLE_NAME)) <> ''
  AND PERSON_LAST_NAME IS NOT NULL
  AND PERSON_LAST_NAME NOT LIKE '%[^0-9 ]%'
ORDER BY NEWID();

-- Does Middle Name ever ALSO have digit contamination in these same rows?
SELECT COUNT(*) AS MiddleAlsoContaminated
FROM dbo.Bronze_PII_Table_Consolidated
WHERE UPPER(RECORD_TYPE) = 'PERSON'
  AND PERSON_LAST_NAME NOT LIKE '%[^0-9 ]%'
  AND PERSON_MIDDLE_NAME LIKE '%[0-9]%';


-- Total volume of this pattern
SELECT COUNT(*) AS FullNameOnlyRecords
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PERSON_FULL_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FULL_NAME)) <> ''
  AND (PERSON_FIRST_NAME IS NULL OR LTRIM(RTRIM(PERSON_FIRST_NAME)) = '')
  AND (PERSON_LAST_NAME IS NULL OR LTRIM(RTRIM(PERSON_LAST_NAME)) = '');

-- Break down by structural shape: comma-separated vs space-separated vs single-token
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

-- Sample the "four+ tokens" bucket specifically - this is where Tola's Hispanic-surname concern lives
SELECT TOP 30 PERSON_FULL_NAME
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PERSON_FULL_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FULL_NAME)) <> ''
  AND (PERSON_FIRST_NAME IS NULL OR LTRIM(RTRIM(PERSON_FIRST_NAME)) = '')
  AND (PERSON_LAST_NAME IS NULL OR LTRIM(RTRIM(PERSON_LAST_NAME)) = '')
  AND LEN(PERSON_FULL_NAME) - LEN(REPLACE(PERSON_FULL_NAME, ' ', '')) >= 3
ORDER BY NEWID();

-- Sample the comma-separated bucket - this is what Melissa's rule targets most directly
SELECT TOP 30 PERSON_FULL_NAME
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PERSON_FULL_NAME LIKE '%,%'
  AND (PERSON_FIRST_NAME IS NULL OR LTRIM(RTRIM(PERSON_FIRST_NAME)) = '')
  AND (PERSON_LAST_NAME IS NULL OR LTRIM(RTRIM(PERSON_LAST_NAME)) = '')
ORDER BY NEWID();

SELECT
    CASE
        WHEN PERSON_FIRST_NAME LIKE '[0-9]%' THEN 'Starts with digit'
        WHEN PERSON_FIRST_NAME LIKE '%[0-9]' THEN 'Ends with digit'
        ELSE 'Digit embedded mid-string'
    END AS DigitPosition,
    COUNT(*) AS RecordCount
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PERSON_FIRST_NAME LIKE '%[0-9]%'
GROUP BY
    CASE
        WHEN PERSON_FIRST_NAME LIKE '[0-9]%' THEN 'Starts with digit'
        WHEN PERSON_FIRST_NAME LIKE '%[0-9]' THEN 'Ends with digit'
        ELSE 'Digit embedded mid-string'
    END;
