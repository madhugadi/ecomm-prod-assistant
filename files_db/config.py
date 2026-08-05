IF OBJECT_ID('dbo.Load_Bronze_Raw_To_Consolidated_With_Checks_TEST', 'P') IS NOT NULL
    DROP PROCEDURE dbo.Load_Bronze_Raw_To_Consolidated_With_Checks_TEST;
GO

CREATE PROCEDURE [dbo].[Load_Bronze_Raw_To_Consolidated_With_Checks_TEST]
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @LoadedBy NVARCHAR(100) = N'Melissa';
    DECLARE @RawRecordCount BIGINT, @UniqueRawRecordCount BIGINT, @ExistingConsolidatedCount BIGINT;
    DECLARE @InsertedConsolidated BIGINT, @ExcludedHard BIGINT;

    SELECT @RawRecordCount = COUNT_BIG(*) FROM dbo.Bronze_PII_Table_Raw;
    SELECT @UniqueRawRecordCount = COUNT_BIG(DISTINCT BRONZE_ROW_HASH) FROM dbo.Bronze_PII_Table_Raw;
    SELECT @ExistingConsolidatedCount = COUNT_BIG(*) FROM dbo.Bronze_PII_Table_Consolidated_TEST;

    IF OBJECT_ID('tempdb..#Deduped') IS NOT NULL DROP TABLE #Deduped;
    IF OBJECT_ID('tempdb..#Checked') IS NOT NULL DROP TABLE #Checked;

    BEGIN TRY
        BEGIN TRANSACTION;

        ------------------------------------------------------------------
        -- STEP 1: Dedup
        ------------------------------------------------------------------
        ;WITH RankedRawRecords AS
        (
            SELECT R.*,
                   ROW_NUMBER() OVER (PARTITION BY R.BRONZE_ROW_HASH ORDER BY R.STAGING_ID) AS DedupRowNum
            FROM dbo.Bronze_PII_Table_Raw AS R
        )
        SELECT *
        INTO #Deduped
        FROM RankedRawRecords
        WHERE DedupRowNum = 1
          AND NOT EXISTS (SELECT 1 FROM dbo.Bronze_PII_Table_Consolidated_TEST AS C
                           WHERE C.BRONZE_ROW_HASH = RankedRawRecords.BRONZE_ROW_HASH)
        OPTION (RECOMPILE);

        CREATE CLUSTERED INDEX IX_Deduped_Hash ON #Deduped (BRONZE_ROW_HASH);

        ------------------------------------------------------------------
        -- STEP 2: Person_ID correction + checks
        -- Company Info (ET1) now uses STRING_SPLIT for exact whole-word
        -- matching, so keywords embedded inside real names (e.g. "INC"
        -- inside "Vincent"/"Lincoln", "CORP" inside "Corpus") no longer
        -- false-positive.
        ------------------------------------------------------------------
        SELECT
            D.*,

            CASE WHEN (D.PERSON_ID LIKE '[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]'
                        OR (D.PERSON_ID NOT LIKE '%[^0-9]%' AND LEN(D.PERSON_ID) = 9))
                      AND (D.PERSON_TAX_ID IS NULL OR LTRIM(RTRIM(D.PERSON_TAX_ID)) = '')
                 THEN NULL ELSE D.PERSON_ID END AS Corrected_PERSON_ID,
            CASE WHEN (D.PERSON_ID LIKE '[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]'
                        OR (D.PERSON_ID NOT LIKE '%[^0-9]%' AND LEN(D.PERSON_ID) = 9))
                      AND (D.PERSON_TAX_ID IS NULL OR LTRIM(RTRIM(D.PERSON_TAX_ID)) = '')
                 THEN D.PERSON_ID ELSE D.PERSON_TAX_ID END AS Corrected_PERSON_TAX_ID,

            CASE WHEN D.PERSON_DATE_OF_BIRTH IS NOT NULL AND D.PERSON_DATE_OF_BIRTH < '1900-01-01'
                 THEN 1 ELSE 0 END AS Fails_ET7_DOBPre1900,

            CASE WHEN D.PERSON_ADDRESS_FULL LIKE '0x%' THEN 1 ELSE 0 END AS Fails_ET11_AddressHex,

            CASE WHEN (D.PERSON_ADDRESS_STREET IS NOT NULL AND D.PERSON_ADDRESS_STREET LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                    OR (D.PERSON_ADDRESS_LINE2 IS NOT NULL AND D.PERSON_ADDRESS_LINE2 LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                    OR (D.PERSON_ADDRESS_CITY IS NOT NULL AND D.PERSON_ADDRESS_CITY LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                    OR (D.PERSON_ADDRESS_STATE IS NOT NULL AND D.PERSON_ADDRESS_STATE LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                    OR (D.PERSON_ADDRESS_ZIP IS NOT NULL AND D.PERSON_ADDRESS_ZIP LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                    OR (D.PERSON_ADDRESS_COUNTRY IS NOT NULL AND D.PERSON_ADDRESS_COUNTRY LIKE '%[<>{}\[\]^~`|@*=_]%' ESCAPE '\')
                 THEN 1 ELSE 0 END AS Fails_ET12_AddressSymbols,

            CASE WHEN (
                    (D.PERSON_FIRST_NAME IS NOT NULL AND LTRIM(RTRIM(D.PERSON_FIRST_NAME)) NOT IN ('','.','-')
                        AND (D.PERSON_FIRST_NAME NOT LIKE '%[^0-9 .,-]%'
                             OR (LEN(D.PERSON_FIRST_NAME) - LEN(REPLACE(TRANSLATE(D.PERSON_FIRST_NAME,'0123456789','##########'),'#',''))) * 2 >= LEN(D.PERSON_FIRST_NAME)))
                 OR (D.PERSON_MIDDLE_NAME IS NOT NULL AND LTRIM(RTRIM(D.PERSON_MIDDLE_NAME)) NOT IN ('','.','-')
                        AND (D.PERSON_MIDDLE_NAME NOT LIKE '%[^0-9 .,-]%'
                             OR (LEN(D.PERSON_MIDDLE_NAME) - LEN(REPLACE(TRANSLATE(D.PERSON_MIDDLE_NAME,'0123456789','##########'),'#',''))) * 2 >= LEN(D.PERSON_MIDDLE_NAME)))
                 OR (D.PERSON_LAST_NAME IS NOT NULL AND LTRIM(RTRIM(D.PERSON_LAST_NAME)) NOT IN ('','.','-')
                        AND (D.PERSON_LAST_NAME NOT LIKE '%[^0-9 .,-]%'
                             OR (LEN(D.PERSON_LAST_NAME) - LEN(REPLACE(TRANSLATE(D.PERSON_LAST_NAME,'0123456789','##########'),'#',''))) * 2 >= LEN(D.PERSON_LAST_NAME)))
                 OR (D.PERSON_FULL_NAME IS NOT NULL AND LTRIM(RTRIM(D.PERSON_FULL_NAME)) NOT IN ('','.','-')
                        AND (D.PERSON_FULL_NAME NOT LIKE '%[^0-9 .,-]%'
                             OR (LEN(D.PERSON_FULL_NAME) - LEN(REPLACE(TRANSLATE(D.PERSON_FULL_NAME,'0123456789','##########'),'#',''))) * 2 >= LEN(D.PERSON_FULL_NAME)))
            ) THEN 1 ELSE 0 END AS Fails_ET3_InvalidName,

            -- ET1: Company Info - exact whole-word match via STRING_SPLIT
            CASE WHEN UPPER(D.RECORD_TYPE) = 'PERSON' AND (
                EXISTS (SELECT 1 FROM STRING_SPLIT(REPLACE(REPLACE(REPLACE(ISNULL(D.PERSON_FIRST_NAME,''),'.',' '),',',' '),'-',' '), ' ') AS w
                        WHERE UPPER(w.value) IN ('LLC','INC','CORP','LTD','DBA','GROUP','ENTERPRISE','PARTNERS','PARTNERSHIP','ASSOCIATES','DISTRICT','SCHOOL','DEPARTMENT'))
             OR EXISTS (SELECT 1 FROM STRING_SPLIT(REPLACE(REPLACE(REPLACE(ISNULL(D.PERSON_MIDDLE_NAME,''),'.',' '),',',' '),'-',' '), ' ') AS w
                        WHERE UPPER(w.value) IN ('LLC','INC','CORP','LTD','DBA','GROUP','ENTERPRISE','PARTNERS','PARTNERSHIP','ASSOCIATES','DISTRICT','SCHOOL','DEPARTMENT'))
             OR EXISTS (SELECT 1 FROM STRING_SPLIT(REPLACE(REPLACE(REPLACE(ISNULL(D.PERSON_LAST_NAME,''),'.',' '),',',' '),'-',' '), ' ') AS w
                        WHERE UPPER(w.value) IN ('LLC','INC','CORP','LTD','DBA','GROUP','ENTERPRISE','PARTNERS','PARTNERSHIP','ASSOCIATES','DISTRICT','SCHOOL','DEPARTMENT'))
             OR EXISTS (SELECT 1 FROM STRING_SPLIT(REPLACE(REPLACE(REPLACE(ISNULL(D.PERSON_FULL_NAME,''),'.',' '),',',' '),'-',' '), ' ') AS w
                        WHERE UPPER(w.value) IN ('LLC','INC','CORP','LTD','DBA','GROUP','ENTERPRISE','PARTNERS','PARTNERSHIP','ASSOCIATES','DISTRICT','SCHOOL','DEPARTMENT'))
             OR D.PERSON_FIRST_NAME LIKE '%&%' OR D.PERSON_MIDDLE_NAME LIKE '%&%' OR D.PERSON_LAST_NAME LIKE '%&%' OR D.PERSON_FULL_NAME LIKE '%&%'
             OR D.PERSON_FIRST_NAME LIKE '%#[0-9]%' OR D.PERSON_LAST_NAME LIKE '%#[0-9]%' OR D.PERSON_FULL_NAME LIKE '%#[0-9]%'
            ) THEN 1 ELSE 0 END AS Fails_ET1_CompanyInfo,

            -- ET2: Digit-Prefixed Name
            CASE WHEN UPPER(D.RECORD_TYPE) = 'PERSON'
                      AND (D.PERSON_FIRST_NAME LIKE '[0-9]%' OR D.PERSON_MIDDLE_NAME LIKE '[0-9]%'
                           OR D.PERSON_LAST_NAME LIKE '[0-9]%' OR D.PERSON_FULL_NAME LIKE '[0-9]%')
                 THEN 1 ELSE 0 END AS Fails_ET2_DigitPrefix

        INTO #Checked
        FROM #Deduped AS D;

        ALTER TABLE #Checked ADD
            AnyHard AS (CASE WHEN Fails_ET1_CompanyInfo=1 OR Fails_ET2_DigitPrefix=1 OR Fails_ET3_InvalidName=1
                                OR Fails_ET7_DOBPre1900=1 OR Fails_ET11_AddressHex=1 OR Fails_ET12_AddressSymbols=1
                           THEN 1 ELSE 0 END);

        ------------------------------------------------------------------
        -- STEP 3: Insert into Consolidated_TEST
        -- ETL_LOAD_DATE direct pass-through (Raw is NOT NULL, no fallback needed)
        ------------------------------------------------------------------
        INSERT INTO dbo.Bronze_PII_Table_Consolidated_TEST
        (
            BRONZE_ID, FILE_NAME, RECORD_TYPE, BOOL_PERSONAL_DATA,
            PERSON_FULL_NAME, PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_SUFFIX,
            PERSON_ID, PERSON_ID_TYPE, PERSON_EMAIL, PERSON_PHONE, PERSON_COMPANY,
            PERSON_DATE_OF_BIRTH, PERSON_TAX_ID,
            PERSON_ADDRESS_FULL, PERSON_ADDRESS_STREET, PERSON_ADDRESS_LINE2, PERSON_ADDRESS_CITY,
            PERSON_ADDRESS_STATE, PERSON_ADDRESS_ZIP, PERSON_ADDRESS_COUNTRY,
            FULL_CREDIT_CARD, CC_CVV, CC_EXPIRATION, USERNAME, PASSWORD,
            DRIVERS_LICENSE, PASSPORT, MILITARY_ID, GOVERNMENT_ID,
            BANK_ACCOUNT_NUMBER, BANK_ROUTING_NUMBER,
            BOOL_EMPLOYEE_COMPENSATION, BOOL_BIOMETRIC_DATA, BOOL_DIGITAL_SIGNATURE,
            BOOL_PERSONAL_CHARACTERISTICS, BOOL_HEALTH_INFO, BOOL_END_USER_CONTRACT,
            JURISDICTION, GEOLOCATION, ETL_LOAD_DATE, ETL_LLM_RATIONALE,
            BRONZE_ROW_HASH, BRONZE_LOAD_DATE, BRONZE_LOAD_BY, RECORD_ID
        )
        SELECT
            REPLACE(CONVERT(CHAR(36), NEWID()), '-', ''),
            C.FILE_NAME, C.RECORD_TYPE, C.BOOL_PERSONAL_DATA,
            C.PERSON_FULL_NAME, C.PERSON_FIRST_NAME, C.PERSON_MIDDLE_NAME, C.PERSON_LAST_NAME, C.PERSON_SUFFIX,
            C.Corrected_PERSON_ID, C.PERSON_ID_TYPE, C.PERSON_EMAIL, C.PERSON_PHONE, C.PERSON_COMPANY,
            C.PERSON_DATE_OF_BIRTH, C.Corrected_PERSON_TAX_ID,
            C.PERSON_ADDRESS_FULL, C.PERSON_ADDRESS_STREET, C.PERSON_ADDRESS_LINE2, C.PERSON_ADDRESS_CITY,
            C.PERSON_ADDRESS_STATE, C.PERSON_ADDRESS_ZIP, C.PERSON_ADDRESS_COUNTRY,
            C.FULL_CREDIT_CARD, C.CC_CVV, C.CC_EXPIRATION, C.USERNAME, C.PASSWORD,
            C.DRIVERS_LICENSE, C.PASSPORT, C.MILITARY_ID, C.GOVERNMENT_ID,
            C.BANK_ACCOUNT_NUMBER, C.BANK_ROUTING_NUMBER,
            C.BOOL_EMPLOYEE_COMPENSATION, C.BOOL_BIOMETRIC_DATA, C.BOOL_DIGITAL_SIGNATURE,
            C.BOOL_PERSONAL_CHARACTERISTICS, C.BOOL_HEALTH_INFO, C.BOOL_END_USER_CONTRACT,
            C.JURISDICTION, C.GEOLOCATION, C.ETL_LOAD_DATE, C.ETL_LLM_RATIONALE,
            C.BRONZE_ROW_HASH, SYSDATETIME(), @LoadedBy, C.RECORD_ID
        FROM #Checked AS C
        WHERE C.AnyHard = 0;

        SET @InsertedConsolidated = @@ROWCOUNT;

        ------------------------------------------------------------------
        -- STEP 4: Insert into Errors_TEST
        -- ETL_LOAD_DATE included as direct pass-through
        ------------------------------------------------------------------
        INSERT INTO dbo.Bronze_PII_Errors_TEST
        (
            ERROR_ID, STAGING_ID, FILE_NAME, RECORD_TYPE, BOOL_PERSONAL_DATA, PERSON_FULL_NAME,
            PERSON_FIRST_NAME, PERSON_MIDDLE_NAME, PERSON_LAST_NAME, PERSON_SUFFIX, PERSON_ID,
            PERSON_ID_TYPE, PERSON_EMAIL, PERSON_PHONE, PERSON_COMPANY, PERSON_DATE_OF_BIRTH,
            PERSON_TAX_ID, PERSON_ADDRESS_FULL, PERSON_ADDRESS_STREET, PERSON_ADDRESS_LINE2,
            PERSON_ADDRESS_CITY, PERSON_ADDRESS_STATE, PERSON_ADDRESS_ZIP, PERSON_ADDRESS_COUNTRY,
            FULL_CREDIT_CARD, CC_CVV, CC_EXPIRATION, USERNAME, PASSWORD, DRIVERS_LICENSE, PASSPORT,
            MILITARY_ID, GOVERNMENT_ID, BANK_ACCOUNT_NUMBER, BANK_ROUTING_NUMBER,
            BOOL_EMPLOYEE_COMPENSATION, BOOL_BIOMETRIC_DATA, BOOL_DIGITAL_SIGNATURE,
            BOOL_PERSONAL_CHARACTERISTICS, BOOL_HEALTH_INFO, BOOL_END_USER_CONTRACT, RECORD_ID,
            JURISDICTION, GEOLOCATION, ETL_TOOLKIT, BATCH_CODE, ETL_LOADED_BY, ETL_LOAD_DATE, BRONZE_ROW_HASH,
            BRONZE_RAW_LOAD_DATE, BRONZE_RAW_LOADED_BY, ERROR_TYPE, ERROR_SEVERITY, ERROR_STAGE,
            ERROR_LOAD_DATE, ERROR_LOADED_BY
        )
        SELECT
            REPLACE(CONVERT(CHAR(36), NEWID()), '-', ''),
            C.STAGING_ID, C.FILE_NAME, C.RECORD_TYPE, C.BOOL_PERSONAL_DATA, C.PERSON_FULL_NAME,
            C.PERSON_FIRST_NAME, C.PERSON_MIDDLE_NAME, C.PERSON_LAST_NAME, C.PERSON_SUFFIX, C.PERSON_ID,
            C.PERSON_ID_TYPE, C.PERSON_EMAIL, C.PERSON_PHONE, C.PERSON_COMPANY, C.PERSON_DATE_OF_BIRTH,
            C.PERSON_TAX_ID, C.PERSON_ADDRESS_FULL, C.PERSON_ADDRESS_STREET, C.PERSON_ADDRESS_LINE2,
            C.PERSON_ADDRESS_CITY, C.PERSON_ADDRESS_STATE, C.PERSON_ADDRESS_ZIP, C.PERSON_ADDRESS_COUNTRY,
            C.FULL_CREDIT_CARD, C.CC_CVV, C.CC_EXPIRATION, C.USERNAME, C.PASSWORD, C.DRIVERS_LICENSE, C.PASSPORT,
            C.MILITARY_ID, C.GOVERNMENT_ID, C.BANK_ACCOUNT_NUMBER, C.BANK_ROUTING_NUMBER,
            C.BOOL_EMPLOYEE_COMPENSATION, C.BOOL_BIOMETRIC_DATA, C.BOOL_DIGITAL_SIGNATURE,
            C.BOOL_PERSONAL_CHARACTERISTICS, C.BOOL_HEALTH_INFO, C.BOOL_END_USER_CONTRACT, C.RECORD_ID,
            C.JURISDICTION, C.GEOLOCATION, C.ETL_TOOLKIT, C.BATCH_CODE, C.ETL_LOADED_BY, C.ETL_LOAD_DATE, C.BRONZE_ROW_HASH,
            C.BRONZE_RAW_LOAD_DATE, C.BRONZE_RAW_LOADED_BY,
            ET.ErrorType, N'Hard', N'Bronze', SYSDATETIME(), @LoadedBy
        FROM #Checked AS C
        CROSS APPLY (VALUES
            (CASE WHEN C.Fails_ET1_CompanyInfo = 1 THEN 1 END, N'ET1 - Company Info'),
            (CASE WHEN C.Fails_ET2_DigitPrefix = 1 THEN 1 END, N'ET2 - Digit-Prefixed Name'),
            (CASE WHEN C.Fails_ET3_InvalidName = 1 THEN 1 END, N'ET3 - Invalid Name (Code-like)'),
            (CASE WHEN C.Fails_ET7_DOBPre1900 = 1 THEN 1 END, N'ET7 - DOB Before 1900'),
            (CASE WHEN C.Fails_ET11_AddressHex = 1 THEN 1 END, N'ET11 - Corrupt Address (Hex Garbage)'),
            (CASE WHEN C.Fails_ET12_AddressSymbols = 1 THEN 1 END, N'ET12 - Invalid Address (Symbols)')
        ) AS ET(Flag, ErrorType)
        WHERE ET.Flag = 1;

        SELECT @ExcludedHard = COUNT(*) FROM #Checked WHERE AnyHard = 1;

        COMMIT TRANSACTION;

        SELECT
            @RawRecordCount AS BronzeRawRecordCount,
            @UniqueRawRecordCount AS UniqueRawRecordCount,
            @ExistingConsolidatedCount AS ConsolidatedRecordCountBefore,
            @InsertedConsolidated AS RecordsInsertedIntoConsolidated,
            @ExcludedHard AS RecordsExcludedHardFail,
            @ExistingConsolidatedCount + @InsertedConsolidated AS ConsolidatedRecordCountAfter,
            SYSDATETIME() AS LoadCompletedDate,
            @LoadedBy AS BronzeLoadedBy;

    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        IF OBJECT_ID('tempdb..#Deduped') IS NOT NULL DROP TABLE #Deduped;
        IF OBJECT_ID('tempdb..#Checked') IS NOT NULL DROP TABLE #Checked;
        THROW;
    END CATCH;

    IF OBJECT_ID('tempdb..#Deduped') IS NOT NULL DROP TABLE #Deduped;
    IF OBJECT_ID('tempdb..#Checked') IS NOT NULL DROP TABLE #Checked;
END;
GO
