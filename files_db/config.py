IF OBJECT_ID('dbo.sp_Cleanse_Address_BronzeConsolidated', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_Cleanse_Address_BronzeConsolidated;
GO

CREATE PROCEDURE [dbo].[sp_Cleanse_Address_BronzeConsolidated]
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- add new columns if not exists
        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated') AND name = 'PWC_PERSON_ADDRESS_FULL')
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated ADD PWC_PERSON_ADDRESS_FULL NVARCHAR(1000) NULL;

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated') AND name = 'PWC_PERSON_ADDRESS_STATE')
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated ADD PWC_PERSON_ADDRESS_STATE NVARCHAR(100) NULL;

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated') AND name = 'PWC_PERSON_ADDRESS_CITY')
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated ADD PWC_PERSON_ADDRESS_CITY NVARCHAR(200) NULL;

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated') AND name = 'PWC_PERSON_ADDRESS_STREET')
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated ADD PWC_PERSON_ADDRESS_STREET NVARCHAR(500) NULL;

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated') AND name = 'PWC_PERSON_ADDRESS_ZIP')
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated ADD PWC_PERSON_ADDRESS_ZIP NVARCHAR(50) NULL;

        ------------------------------------------------------------------
        -- PERSON_ADDRESS_FULL: URL junk, '#N/A', single-character -> NULL
        ------------------------------------------------------------------
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PWC_PERSON_ADDRESS_FULL =
                CASE
                    WHEN PERSON_ADDRESS_FULL LIKE ''http://%'' OR PERSON_ADDRESS_FULL LIKE ''https://%'' THEN NULL
                    WHEN PERSON_ADDRESS_FULL = ''#N/A'' THEN NULL
                    WHEN LEN(PERSON_ADDRESS_FULL) = 1 THEN NULL
                    ELSE PERSON_ADDRESS_FULL
                END;
        ');

        ------------------------------------------------------------------
        -- PERSON_ADDRESS_STATE: numeric-only, hex, backslash-path,
        -- scientific notation, single-character -> NULL
        ------------------------------------------------------------------
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PWC_PERSON_ADDRESS_STATE =
                CASE
                    WHEN PERSON_ADDRESS_STATE NOT LIKE ''%[^0-9]%'' THEN NULL
                    WHEN PERSON_ADDRESS_STATE LIKE ''0x%'' THEN NULL
                    WHEN CHARINDEX(''\'', PERSON_ADDRESS_STATE) > 0 THEN NULL
                    WHEN PERSON_ADDRESS_STATE LIKE ''%E+%'' THEN NULL
                    WHEN LEN(PERSON_ADDRESS_STATE) = 1 THEN NULL
                    WHEN PERSON_ADDRESS_STATE IN (
                        ''main'',''Stable'',''DATA'',''.text'',''###Uninitialized###'',''###Unitialized###'',
                        '',,,,(default),'',''Full formatting.'',''experimental'',''templproj.txt'',''templproj.a43'',
                        ''Ink0t.xcl'',''Ink0t.icf'',''XX'',''Son.'',''Pa050'',''ePLACED'',''ACTIVE'',
                        ''aaa.bbb.ccc.ddd'',''ewarm''
                    ) THEN NULL
                    ELSE PERSON_ADDRESS_STATE
                END;
        ');

        ------------------------------------------------------------------
        -- PERSON_ADDRESS_CITY: numeric-only, hex, backslash-path,
        -- scientific notation, single-character -> NULL
        ------------------------------------------------------------------
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PWC_PERSON_ADDRESS_CITY =
                CASE
                    WHEN PERSON_ADDRESS_CITY NOT LIKE ''%[^0-9]%'' THEN NULL
                    WHEN PERSON_ADDRESS_CITY LIKE ''0x%'' THEN NULL
                    WHEN CHARINDEX(''\'', PERSON_ADDRESS_CITY) > 0 THEN NULL
                    WHEN PERSON_ADDRESS_CITY LIKE ''%E+%'' THEN NULL
                    WHEN LEN(PERSON_ADDRESS_CITY) = 1 THEN NULL
                    WHEN PERSON_ADDRESS_CITY IN (
                        ''main'',''Stable'',''DATA'',''.text'',''###Uninitialized###'',''###Unitialized###'',
                        '',,,,(default),'',''Full formatting.'',''experimental'',''templproj.txt'',''templproj.a43'',
                        ''Ink0t.xcl'',''Ink0t.icf'',''XX'',''Son.'',''Pa050'',''ePLACED'',''ACTIVE'',
                        ''aaa.bbb.ccc.ddd'',''ewarm''
                    ) THEN NULL
                    ELSE PERSON_ADDRESS_CITY
                END;
        ');

        ------------------------------------------------------------------
        -- PERSON_ADDRESS_STREET: numeric-only, hex, backslash-path,
        -- scientific notation, single-character -> NULL
        ------------------------------------------------------------------
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PWC_PERSON_ADDRESS_STREET =
                CASE
                    WHEN PERSON_ADDRESS_STREET NOT LIKE ''%[^0-9]%'' THEN NULL
                    WHEN PERSON_ADDRESS_STREET LIKE ''0x%'' THEN NULL
                    WHEN CHARINDEX(''\'', PERSON_ADDRESS_STREET) > 0 THEN NULL
                    WHEN PERSON_ADDRESS_STREET LIKE ''%E+%'' THEN NULL
                    WHEN LEN(PERSON_ADDRESS_STREET) = 1 THEN NULL
                    WHEN PERSON_ADDRESS_STREET IN (
                        ''main'',''Stable'',''DATA'',''.text'',''###Uninitialized###'',''###Unitialized###'',
                        '',,,,(default),'',''Full formatting.'',''experimental'',''templproj.txt'',''templproj.a43'',
                        ''Ink0t.xcl'',''Ink0t.icf'',''XX'',''Son.'',''Pa050'',''ePLACED'',''ACTIVE'',
                        ''aaa.bbb.ccc.ddd'',''ewarm''
                    ) THEN NULL
                    ELSE PERSON_ADDRESS_STREET
                END;
        ');

        ------------------------------------------------------------------
        -- PERSON_ADDRESS_ZIP: hex, backslash-path, scientific notation,
        -- single-character -> NULL (numeric-only NOT excluded here - valid zips are numeric)
        ------------------------------------------------------------------
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PWC_PERSON_ADDRESS_ZIP =
                CASE
                    WHEN PERSON_ADDRESS_ZIP LIKE ''0x%'' THEN NULL
                    WHEN CHARINDEX(''\'', PERSON_ADDRESS_ZIP) > 0 THEN NULL
                    WHEN PERSON_ADDRESS_ZIP LIKE ''%E+%'' THEN NULL
                    WHEN LEN(PERSON_ADDRESS_ZIP) = 1 THEN NULL
                    ELSE PERSON_ADDRESS_ZIP
                END;
        ');

        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
