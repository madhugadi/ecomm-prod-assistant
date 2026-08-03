SELECT
    '0x000c00b7' AS TestValue, 
    CASE WHEN '0x000c00b7' LIKE '0x%' THEN 'MATCH' ELSE 'NO MATCH' END AS HexCheck
UNION ALL
SELECT 
    '123 Main St. Apt #5 <test>', 
    CASE WHEN '123 Main St. Apt #5 <test>' LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\' THEN 'MATCH' ELSE 'NO MATCH' END
UNION ALL
SELECT
    'Normal Address No Symbols',
    CASE WHEN 'Normal Address No Symbols' LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\' THEN 'MATCH' ELSE 'NO MATCH' END;

    SELECT TOP 20 PERSON_ADDRESS_FULL
FROM dbo.Bronze_PII_Table_Raw
WHERE PERSON_ADDRESS_FULL LIKE '0x%'
ORDER BY NEWID();
