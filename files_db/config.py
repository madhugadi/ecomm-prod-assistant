IF OBJECT_ID('tempdb..#ConsolidatedEmails') IS NOT NULL DROP TABLE #ConsolidatedEmails;

SELECT DISTINCT PWC_PERSON_EMAIL AS Email
INTO #ConsolidatedEmails
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PWC_PERSON_EMAIL IS NOT NULL;

CREATE CLUSTERED INDEX IX_TempEmails ON #ConsolidatedEmails (Email);

SELECT COUNT(*) AS FillableRecords
FROM dbo.Bronze_PII_Table_Consolidated c
JOIN #ConsolidatedEmails t ON t.Email = c.PWC_PERSON_EMAIL
JOIN dbo.ITR_Work_Home_Address_Audit a
    ON a.Email_Work = t.Email OR a.Email_Home = t.Email
WHERE (c.PWC_PERSON_ADDRESS_CITY IS NULL AND a.Primary_Address_City IS NOT NULL)
   OR (c.PWC_PERSON_ADDRESS_STATE IS NULL AND COALESCE(a.Primary_Home_Address_State, a.Primary_Address_State_Province) IS NOT NULL)
   OR (c.PWC_PERSON_ADDRESS_COUNTRY IS NULL AND a.Primary_Home_Address_Country IS NOT NULL);

DROP TABLE #ConsolidatedEmails;
