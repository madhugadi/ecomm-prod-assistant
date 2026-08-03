SELECT
    COUNT(*) AS TotalNonNullEmail,

    SUM(CASE WHEN PERSON_EMAIL NOT LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END) AS Hard_NoLettersAtAll,

    SUM(CASE WHEN PERSON_EMAIL NOT LIKE '%@%'
              AND PERSON_EMAIL LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END) AS Hard_NoAtSign_ButHasLetters,

    SUM(CASE WHEN PERSON_EMAIL LIKE '%@%'
              AND PERSON_EMAIL LIKE '%[a-zA-Z]%'
              AND (
                    PERSON_EMAIL LIKE '%@%@%'
                 OR PERSON_EMAIL LIKE '% %'
                 OR PERSON_EMAIL NOT LIKE '_%@_%.__%'
              )
        THEN 1 ELSE 0 END) AS Soft_HasAtAndLetters_ButMalformed

FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_EMAIL IS NOT NULL AND LTRIM(RTRIM(PERSON_EMAIL)) <> '';
