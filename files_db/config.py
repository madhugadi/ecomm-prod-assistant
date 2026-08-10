-- Step 1: How many audit table emails actually match a Consolidated record at all?
SELECT COUNT(DISTINCT a.Employee_ID) AS AuditRowsWithAnyMatch
FROM dbo.ITR_Work_Home_Address_Audit a
WHERE EXISTS (
    SELECT 1 FROM dbo.Bronze_PII_Table_Consolidated c
    WHERE c.PERSON_EMAIL = a.Email_Work
       OR c.PERSON_EMAIL = a.Email_Home
       OR c.PWC_PERSON_EMAIL = a.Email_Work
       OR c.PWC_PERSON_EMAIL = a.Email_Home
);

-- Step 2: Of those matches, how many Consolidated records currently have NULL address fields
-- that the audit table could actually fill in?
SELECT COUNT(*) AS FillableRecords
FROM dbo.Bronze_PII_Table_Consolidated c
JOIN dbo.ITR_Work_Home_Address_Audit a
    ON a.Email_Work = c.PERSON_EMAIL OR a.Email_Home = c.PERSON_EMAIL
    OR a.Email_Work = c.PWC_PERSON_EMAIL OR a.Email_Home = c.PWC_PERSON_EMAIL
WHERE (c.PWC_PERSON_ADDRESS_CITY IS NULL AND a.City IS NOT NULL)
   OR (c.PWC_PERSON_ADDRESS_STATE IS NULL AND a.State IS NOT NULL)
   OR (c.PWC_PERSON_ADDRESS_COUNTRY IS NULL AND a.Primary_Home_Address_Country IS NOT NULL);

-- Step 3: Sample the actual matched rows so we can eyeball data quality
SELECT TOP 30
    c.PERSON_EMAIL, c.PWC_PERSON_EMAIL,
    c.PWC_PERSON_ADDRESS_CITY, a.City,
    c.PWC_PERSON_ADDRESS_STATE, a.State,
    c.PWC_PERSON_ADDRESS_COUNTRY, a.Primary_Home_Address_Country
FROM dbo.Bronze_PII_Table_Consolidated c
JOIN dbo.ITR_Work_Home_Address_Audit a
    ON a.Email_Work = c.PERSON_EMAIL OR a.Email_Home = c.PERSON_EMAIL
    OR a.Email_Work = c.PWC_PERSON_EMAIL OR a.Email_Home = c.PWC_PERSON_EMAIL
ORDER BY NEWID();
