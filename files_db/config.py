Data Type Checks Summary
Column	Check	Hard (excluded from Consolidated)	Soft (still goes to Consolidated)
First Name	Digits/special characters	No letters at all	Has letters + digit/symbol
Middle Name	Digits/special characters	No letters at all	Has letters + digit/symbol
Last Name	Digits/special characters	No letters at all	Has letters + digit/symbol
Email	Format validation	No @ sign, or no letters at all	Has @ and letters, but still malformed
Date of Birth	Future date or before 1900-01-01	Always Hard (no soft tier)	—
Tax ID	Format/garbage check	Placeholder or garbage characters	Too short but alphanumeric
Address (all sub-fields)	Special characters	Hex-garbage pattern (0x...)	Other disallowed symbols
Person_First/Middle/Last Name	Company-like keywords (LLC, INC, CORP, DBA, etc.)	Always Hard — RECORD_TYPE = Person only	—
Person_ID_Type	—	Not checked (informational only)	—
Person_ID	If SSN pattern found → moved to Tax_ID, cleared from Person_ID	Correction, not a check	—

Rule: Hard → record excluded from Consolidated, goes to Errors only. Soft → record still goes to Consolidated, also logged in Errors for visibility.
