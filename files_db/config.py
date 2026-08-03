Final Rule Book — Locked
Error Type	Columns	Trigger	Severity
ET1	First/Middle/Last/Full Name	Company keywords	Hard
ET2	First/Middle/Last/Full Name	Digit-prefixed	Hard
ET3	First/Middle/Last/Full Name	Code-like (no letters or digit-dominant)	Hard
ET4	First/Middle/Last/Full Name	Minor issue (letters dominant, some digit/symbol)	Soft
ET5	Email	[none]	Hard
ET6	Email	Other format failure	Soft
ET7	DOB	Pre-1900	Hard
ET8	DOB	Future date	Soft
ET9	Tax ID	Garbage/placeholder	Hard
ET10	Tax ID	Too short	Soft
ET11	Address Full only	Hex-garbage (0x...)	Hard
ET12	Street/Line2/City/State/Zip/Country	Disallowed symbols	Hard

Not checked: Person_ID_Type
Correction only: Person_ID → Tax_ID

This is the complete, final rule book. Ready to write the stored procedure now — incorporating Full Name into the Name and Company Info/Digit-Prefix checks, with all 12 error types correctly routed. Want me to proceed with the full proc?

how does these error types look in error table, i mean et1 et2 et3 etc..

Here's exactly how the ERROR_TYPE values would look as actual data in the Bronze_PII_Errors table.

Format

Each row's ERROR_TYPE column holds a single text value combining the code and a short description — matching the format Melissa specifically asked for: "ET# - [Error]"

ERROR_TYPE (as stored)	ERROR_SEVERITY
ET1 - Company Info	Hard
ET2 - Digit-Prefixed Name	Hard
ET3 - Invalid Name (Code-like)	Hard
ET4 - Invalid Name Characters	Soft
ET5 - Email Placeholder/None	Hard
ET6 - Invalid Email Format	Soft
ET7 - DOB Before 1900	Hard
ET8 - DOB In Future	Soft
ET9 - Invalid Tax ID (Garbage)	Hard
ET10 - Invalid Tax ID (Too Short)	Soft
ET11 - Corrupt Address (Hex Garbage)	Hard
ET12 - Invalid Address (Symbols)	Hard
Example: what a few actual rows in the Errors table would look like
ERROR_ID	PERSON_FIRST_NAME	PERSON_LAST_NAME	PERSON_ADDRESS_FULL	ERROR_TYPE	ERROR_SEVERITY	ERROR_STAGE
a1b2c3...	NULL	434100 FAMILY DOLLAR	...	ET1 - Company Info	Hard	Bronze
d4e5f6...	John	Smith2	...	ET4 - Invalid Name Characters	Soft	Bronze
g7h8i9...	NULL	NULL	0x000c00b7	ET11 - Corrupt Address (Hex Garbage)	Hard	Bronze
