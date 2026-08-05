/******************************************************************************
 Validation Queries - Bronze Data Quality Checks Stored Proc Test Run
 Run these against the _TEST tables after executing:
 dbo.Load_Bronze_Raw_To_Consolidated_With_Checks_TEST
******************************************************************************/

-- ============================================================
-- 1. OVERALL COUNTS
-- Sanity check: Consolidated + unique records in Errors should
-- roughly equal unique Raw records (nothing lost or duplicated)
-- ============================================================
SELECT
    (SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Raw) AS TotalRaw,
    (SELECT COUNT(DISTINCT BRONZE_ROW_HASH) FROM dbo.Bronze_PII_Table_Raw) AS UniqueRaw,
    (SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated_TEST) AS TotalConsolidated,
    (SELECT COUNT(*) FROM dbo.Bronze_PII_Errors_TEST) AS TotalErrorRows,
    (SELECT COUNT(DISTINCT BRONZE_ROW_HASH) FROM dbo.Bronze_PII_Errors_TEST) AS UniqueRecordsInErrors;


-- ============================================================
-- 2. ERROR TYPE BREAKDOWN
-- Compare against known baseline counts from earlier profiling:
-- ET11 (hex-garbage) ~116,570 | ET12 (address symbols) ~96,479
-- ET7 (DOB pre-1900) ~94
-- ============================================================
SELECT ERROR_TYPE, COUNT(*) AS RecordCount
FROM dbo.Bronze_PII_Errors_TEST
GROUP BY ERROR_TYPE
ORDER BY RecordCount DESC;


-- ============================================================
-- 3. SAMPLE REAL VALUES PER ERROR TYPE
-- Eyeball actual data to confirm each check is catching real issues,
-- not false positives
-- ============================================================

-- ET1 - Company Info
SELECT TOP 10 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET1 - Company Info' ORDER BY NEWID();

-- ET2 - Digit-Prefixed Name
SELECT TOP 10 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET2 - Digit-Prefixed Name' ORDER BY NEWID();

-- ET3 - Invalid Name (Code-like)
SELECT TOP 10 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET3 - Invalid Name (Code-like)' ORDER BY NEWID();

-- ET7 - DOB Before 1900
SELECT TOP 10 PERSON_DATE_OF_BIRTH, PERSON_FIRST_NAME, PERSON_LAST_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET7 - DOB Before 1900' ORDER BY NEWID();

-- ET11 - Corrupt Address (Hex Garbage)
SELECT TOP 10 PERSON_ADDRESS_FULL, PERSON_FIRST_NAME, PERSON_LAST_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET11 - Corrupt Address (Hex Garbage)' ORDER BY NEWID();

-- ET12 - Invalid Address (Symbols)
SELECT TOP 10 PERSON_ADDRESS_STREET, PERSON_ADDRESS_CITY, PERSON_ADDRESS_STATE, PERSON_ADDRESS_ZIP, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST WHERE ERROR_TYPE = 'ET12 - Invalid Address (Symbols)' ORDER BY NEWID();


-- ============================================================
-- 4. HEX-GARBAGE ADDRESS SHOULD NOT ALSO EXIST IN CONSOLIDATED
-- ============================================================
SELECT TOP 5 * FROM dbo.Bronze_PII_Errors_TEST WHERE PERSON_ADDRESS_FULL LIKE '0x%';

SELECT COUNT(*) AS ShouldBeZero
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_ADDRESS_FULL LIKE '0x%';


-- ============================================================
-- 5. RECORDS THAT SHOULD PASS - confirm they landed in Consolidated
-- ============================================================

-- Minor name issues (e.g. John2) - no longer flagged, should pass through
SELECT TOP 10 PERSON_FIRST_NAME, PERSON_LAST_NAME
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_FIRST_NAME LIKE '%[a-zA-Z]%[0-9]%' ORDER BY NEWID();

-- '.' or '-' as a name placeholder - should be treated as NULL-equivalent, not excluded
SELECT TOP 10 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_FIRST_NAME IN ('.','-') OR PERSON_MIDDLE_NAME IN ('.','-') ORDER BY NEWID();

-- Future DOB - passes through under simplified rules
SELECT TOP 10 PERSON_DATE_OF_BIRTH, PERSON_FIRST_NAME, PERSON_LAST_NAME
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_DATE_OF_BIRTH > CAST(GETDATE() AS DATE) ORDER BY NEWID();


-- ============================================================
-- 6. NON-LATIN SCRIPT NAMES (Chinese/Japanese/Greek/etc.)
-- Must pass through to Consolidated (Unicode fix), and must NOT
-- appear in Errors as ET3 - Invalid Name (Code-like)
-- ============================================================

-- Should return rows (correctly passed)
SELECT TOP 15 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE (PERSON_FIRST_NAME IS NOT NULL AND PERSON_FIRST_NAME NOT LIKE '%[a-zA-Z0-9]%')
   OR (PERSON_LAST_NAME IS NOT NULL AND PERSON_LAST_NAME NOT LIKE '%[a-zA-Z0-9]%')
   OR (PERSON_FULL_NAME IS NOT NULL AND PERSON_FULL_NAME NOT LIKE '%[a-zA-Z0-9]%')
ORDER BY NEWID();

-- Should return few or zero rows (would indicate the Unicode fix failed)
SELECT TOP 15 PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_FULL_NAME, ERROR_TYPE
FROM dbo.Bronze_PII_Errors_TEST
WHERE (PERSON_FIRST_NAME IS NOT NULL AND PERSON_FIRST_NAME NOT LIKE '%[a-zA-Z0-9]%')
   OR (PERSON_LAST_NAME IS NOT NULL AND PERSON_LAST_NAME NOT LIKE '%[a-zA-Z0-9]%')
   OR (PERSON_FULL_NAME IS NOT NULL AND PERSON_FULL_NAME NOT LIKE '%[a-zA-Z0-9]%')
ORDER BY NEWID();


-- ============================================================
-- 7. PERSON_ID -> TAX_ID CORRECTION
-- Confirms the move-and-clear logic actually ran
-- ============================================================
SELECT TOP 10 PERSON_ID, PERSON_TAX_ID
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_TAX_ID LIKE '[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]'
  AND PERSON_ID IS NULL;


-- ============================================================
-- 8. TAX ID - CONFIRM NO VALIDATION APPLIED (expected, by design)
-- Garbage/placeholder Tax IDs should pass through untouched
-- ============================================================
SELECT TOP 10 PERSON_TAX_ID, PERSON_FIRST_NAME, PERSON_LAST_NAME
FROM dbo.Bronze_PII_Table_Consolidated_TEST
WHERE PERSON_TAX_ID IN ('000000000','123456789','111111111','999999999');
