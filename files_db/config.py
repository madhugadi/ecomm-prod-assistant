SELECT
    'FirstName' AS ColumnChecked,
    SUM(CASE WHEN PERSON_FIRST_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_FIRST_NAME LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END) AS Soft_MixedWithLetters,
    SUM(CASE WHEN PERSON_FIRST_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_FIRST_NAME NOT LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END) AS Hard_NoLettersAtAll
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_FIRST_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_FIRST_NAME)) <> ''

UNION ALL

SELECT
    'MiddleName',
    SUM(CASE WHEN PERSON_MIDDLE_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_MIDDLE_NAME LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END),
    SUM(CASE WHEN PERSON_MIDDLE_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_MIDDLE_NAME NOT LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END)
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_MIDDLE_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_MIDDLE_NAME)) <> ''

UNION ALL

SELECT
    'LastName',
    SUM(CASE WHEN PERSON_LAST_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_LAST_NAME LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END),
    SUM(CASE WHEN PERSON_LAST_NAME LIKE '%[0-9!@#$%^*()+=|\/<>{}[]~`_"]%' 
             AND PERSON_LAST_NAME NOT LIKE '%[a-zA-Z]%'
        THEN 1 ELSE 0 END)
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_LAST_NAME IS NOT NULL AND LTRIM(RTRIM(PERSON_LAST_NAME)) <> '';


SELECT
    SUM(CASE WHEN PERSON_TAX_ID IN ('000000000','123456789','111111111','999999999')
              OR PERSON_TAX_ID LIKE '%[^a-zA-Z0-9-]%'
        THEN 1 ELSE 0 END) AS Hard_PlaceholderOrGarbage,
    SUM(CASE WHEN LEN(LTRIM(RTRIM(PERSON_TAX_ID))) < 6
              AND PERSON_TAX_ID NOT LIKE '%[^a-zA-Z0-9-]%'
        THEN 1 ELSE 0 END) AS Soft_TooShortButAlphanumeric
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_TAX_ID IS NOT NULL AND LTRIM(RTRIM(PERSON_TAX_ID)) <> '';


SELECT
    SUM(CASE WHEN PERSON_ADDRESS_FULL LIKE '0x%' THEN 1 ELSE 0 END) AS Hard_HexGarbage,
    SUM(CASE WHEN PERSON_ADDRESS_FULL LIKE '%[<>{}[]^~`|@*=_]%' 
              AND PERSON_ADDRESS_FULL NOT LIKE '0x%'
        THEN 1 ELSE 0 END) AS Soft_OtherSymbolIssues
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_ADDRESS_FULL IS NOT NULL AND LTRIM(RTRIM(PERSON_ADDRESS_FULL)) <> '';
