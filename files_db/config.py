IF OBJECT_ID('dbo.sp_Cleanse_PersonEmail_BronzeConsolidated', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_Cleanse_PersonEmail_BronzeConsolidated;
GO

CREATE PROCEDURE [dbo].[sp_Cleanse_PersonEmail_BronzeConsolidated]
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- add new column if not exists
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
            WHERE object_id = OBJECT_ID('dbo.Bronze_PII_Table_Consolidated')
              AND name = 'PERSON_EMAIL_CLEANED'
        )
        BEGIN
            ALTER TABLE dbo.Bronze_PII_Table_Consolidated
            ADD PERSON_EMAIL_CLEANED NVARCHAR(500) NULL;
        END

        -- pass 1: extract candidate email (strip angle-bracket wrapper, take first of multi-email list)
        -- run via dynamic SQL so the column added above is resolved at runtime, not at proc compile time
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PERSON_EMAIL_CLEANED =
                CASE
                    WHEN PERSON_EMAIL = ''[none]'' THEN NULL
                    WHEN PERSON_EMAIL LIKE ''%<%@%>%''
                        THEN SUBSTRING(PERSON_EMAIL, CHARINDEX(''<'', PERSON_EMAIL) + 1,
                             CHARINDEX(''>'', PERSON_EMAIL) - CHARINDEX(''<'', PERSON_EMAIL) - 1)
                    WHEN PERSON_EMAIL LIKE ''%,%'' AND PERSON_EMAIL LIKE ''%@%''
                        THEN LTRIM(RTRIM(LEFT(PERSON_EMAIL, CHARINDEX('','', PERSON_EMAIL) - 1)))
                    ELSE PERSON_EMAIL
                END;
        ');

        -- pass 2: null out if candidate has no @ at all (covers numbers, names, noise like ''>100 Days'', etc.)
        EXEC(N'
            UPDATE dbo.Bronze_PII_Table_Consolidated
            SET PERSON_EMAIL_CLEANED = NULL
            WHERE PERSON_EMAIL_CLEANED IS NOT NULL
              AND LTRIM(RTRIM(PERSON_EMAIL_CLEANED)) <> ''''
              AND PERSON_EMAIL_CLEANED NOT LIKE ''%@%'';
        ');

        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
