SELECT PWC_PERSON_EMAIL, COUNT(*) AS Cnt
FROM dbo.Bronze_PII_Table_Consolidated
WHERE PWC_PERSON_EMAIL IN (
    SELECT Email_Work FROM dbo.ITR_Work_Home_Address_Audit WHERE Email_Work IS NOT NULL
    UNION
    SELECT Email_Home FROM dbo.ITR_Work_Home_Address_Audit WHERE Email_Home IS NOT NULL
)
GROUP BY PWC_PERSON_EMAIL
ORDER BY Cnt DESC;
