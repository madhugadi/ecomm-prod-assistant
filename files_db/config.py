
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

IF OBJECT_ID('dbo.Bronze_PII_Errors', 'U') IS NOT NULL
    DROP TABLE dbo.Bronze_PII_Errors;
GO

CREATE TABLE dbo.Bronze_PII_Errors
(
    ERROR_ID                        CHAR(32)         NOT NULL,

    -- Mirrors Bronze_PII_Table_Raw columns
    STAGING_ID                      BIGINT           NULL,
    FILE_NAME                       NVARCHAR(500)    NULL,
    RECORD_TYPE                     NVARCHAR(50)     NULL,
    BOOL_PERSONAL_DATA              BIT              NULL,
    PERSON_FULL_NAME                NVARCHAR(500)    NULL,
    PERSON_FIRST_NAME               NVARCHAR(200)    NULL,
    PERSON_MIDDLE_NAME              NVARCHAR(200)    NULL,
    PERSON_LAST_NAME                NVARCHAR(200)    NULL,
    PERSON_SUFFIX                   NVARCHAR(20)     NULL,
    PERSON_ID                       NVARCHAR(100)    NULL,
    PERSON_ID_TYPE                  NVARCHAR(100)    NULL,
    PERSON_EMAIL                    NVARCHAR(500)    NULL,
    PERSON_PHONE                    NVARCHAR(500)    NULL,
    PERSON_COMPANY                  NVARCHAR(500)    NULL,
    PERSON_DATE_OF_BIRTH            DATE             NULL,
    PERSON_TAX_ID                   NVARCHAR(100)    NULL,
    PERSON_ADDRESS_FULL             NVARCHAR(1000)   NULL,
    PERSON_ADDRESS_STREET           NVARCHAR(500)    NULL,
    PERSON_ADDRESS_LINE2            NVARCHAR(500)    NULL,
    PERSON_ADDRESS_CITY             NVARCHAR(200)    NULL,
    PERSON_ADDRESS_STATE            NVARCHAR(100)    NULL,
    PERSON_ADDRESS_ZIP              NVARCHAR(50)     NULL,
    PERSON_ADDRESS_COUNTRY          NVARCHAR(100)    NULL,
    FULL_CREDIT_CARD                NVARCHAR(100)    NULL,
    CC_CVV                          NVARCHAR(100)    NULL,
    CC_EXPIRATION                   NVARCHAR(100)    NULL,
    USERNAME                        NVARCHAR(500)    NULL,
    PASSWORD                        NVARCHAR(500)    NULL,
    DRIVERS_LICENSE                 NVARCHAR(500)    NULL,
    PASSPORT                        NVARCHAR(500)    NULL,
    MILITARY_ID                     NVARCHAR(500)    NULL,
    GOVERNMENT_ID                   NVARCHAR(500)    NULL,
    BANK_ACCOUNT_NUMBER             NVARCHAR(500)    NULL,
    BANK_ROUTING_NUMBER             NVARCHAR(500)    NULL,
    BOOL_EMPLOYEE_COMPENSATION      BIT              NULL,
    BOOL_BIOMETRIC_DATA             BIT              NULL,
    BOOL_DIGITAL_SIGNATURE          BIT              NULL,
    BOOL_PERSONAL_CHARACTERISTICS   BIT              NULL,
    BOOL_HEALTH_INFO                BIT              NULL,
    BOOL_END_USER_CONTRACT          BIT              NULL,
    ETL_LOAD_DATE                   DATETIME2(7)     NULL,
    ETL_LLM_RATIONALE               NVARCHAR(2000)   NULL,
    RECORD_ID                       NVARCHAR(500)    NULL,
    JURISDICTION                    NVARCHAR(500)    NULL,
    GEOLOCATION                     NVARCHAR(500)    NULL,
    ETL_TOOLKIT                     NVARCHAR(100)    NULL,
    BATCH_CODE                      NVARCHAR(250)    NULL,
    ETL_LOADED_BY                   NVARCHAR(250)    NULL,
    BRONZE_ROW_HASH                 CHAR(32)         NULL,
    BRONZE_RAW_LOAD_DATE            DATETIME2(7)     NULL,
    BRONZE_RAW_LOADED_BY            NVARCHAR(250)    NULL,

    -- New error-tracking columns
    ERROR_TYPE                      NVARCHAR(200)    NOT NULL,   -- e.g. 'ET1 - Company Info'
    ERROR_SEVERITY                  NVARCHAR(10)     NOT NULL,   -- 'Hard' or 'Soft'
    ERROR_STAGE                     NVARCHAR(50)     NOT NULL DEFAULT ('Bronze'),
    ERROR_LOAD_DATE                 DATETIME2(3)     NOT NULL DEFAULT (SYSDATETIME()),
    ERROR_LOADED_BY                 NVARCHAR(100)    NOT NULL,

    CONSTRAINT PK_Bronze_PII_Errors PRIMARY KEY (ERROR_ID)
);
GO

CREATE INDEX IX_Bronze_PII_Errors_ErrorType
    ON dbo.Bronze_PII_Errors (ERROR_TYPE, ERROR_SEVERITY, ERROR_LOAD_DATE);
GO

CREATE INDEX IX_Bronze_PII_Errors_RowHash
    ON dbo.Bronze_PII_Errors (BRONZE_ROW_HASH);
GO
