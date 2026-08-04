-- Only copy the tables that get WRITTEN to
SELECT * INTO dbo.Bronze_PII_Table_Consolidated_TEST
FROM dbo.Bronze_PII_Table_Consolidated
WHERE 1=0;

SELECT * INTO dbo.Bronze_PII_Errors_TEST
FROM dbo.Bronze_PII_Errors
WHERE 1=0;
