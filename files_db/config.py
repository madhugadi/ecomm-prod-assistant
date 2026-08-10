IF OBJECT_ID('tempdb..#ConsolidatedEmails') IS NOT NULL DROP TABLE #ConsolidatedEmails;

SELECT DISTINCT PWC_PERSON_EMAIL AS Email
INTO #ConsolidatedEmails
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PWC_PERSON_EMAIL IS NOT NULL;

CREATE CLUSTERED INDEX IX_TempEmails ON #ConsolidatedEmails (Email);

SELECT COUNT(DISTINCT a.Employee_ID) AS AuditRowsWithAnyMatch
FROM dbo.ITR_Work_Home_Address_Audit a
WHERE EXISTS (SELECT 1 FROM #ConsolidatedEmails t WHERE t.Email = a.Email_Work)
   OR EXISTS (SELECT 1 FROM #ConsolidatedEmails t WHERE t.Email = a.Email_Home);

DROP TABLE #ConsolidatedEmails;
