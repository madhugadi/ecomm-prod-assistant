Bronze Raw → Bronze Consolidated Data Type Checks — Final Rule Set
#	Error Type	Check Name	Column(s) Checked	Trigger Condition	Outcome
1	ET1	Company Info	Person First Name, Middle Name, Last Name, Full Name	Contains a standalone word matching: LLC, INC, CORP, LTD, DBA, GROUP, ENTERPRISE, PARTNERS, PARTNERSHIP, ASSOCIATES, DISTRICT, SCHOOL, DEPARTMENT — or contains "&" — or contains "#" followed by digits. Applies only when Record Type = Person. Uses whole-word matching so it does not falsely catch names like "Vincent" or "Lincoln."	Excluded from Consolidated; logged to Errors table only
2	ET2	Digit-Prefixed Name	Person First Name, Middle Name, Last Name, Full Name	Value starts with a digit. Applies only when Record Type = Person.	Excluded from Consolidated; logged to Errors table only
3	ET3	Invalid Name (Code-like)	Person First Name, Middle Name, Last Name, Full Name (checked independently)	Value contains no letters of any language/script at all, OR digits make up 50% or more of the value's length (i.e., looks like a code, not a name). A single "." or "-" is treated the same as blank/missing and does not trigger this check. Blank/missing values are never flagged.	Excluded from Consolidated; logged to Errors table only
4	ET4	DOB Before 1900	Person Date of Birth	Date is earlier than 1900-01-01. Blank/missing values are never flagged.	Excluded from Consolidated; logged to Errors table only
5	ET5	Corrupt Address (Hex Garbage)	Person Address Full	Value starts with "0x" (a corrupted system/binary artifact, not a real address).	Excluded from Consolidated; logged to Errors table only
6	ET6	Invalid Address (Symbols)	Person Address Street, Line 2, City, State, Zip, Country	Value contains any of these characters: < > { } [ ] ^ ~ ` | @ * = _ . Blank/missing values are never flagged. Note: Address Full is not included in this check (only checked for hex garbage above).	Excluded from Consolidated; logged to Errors table only


Checks Reviewed and Intentionally NOT Applied (Pass-Through)
Column(s)	Original Concern	Decision
Person First/Middle/Last/Full Name	Minor issues — a real name with a stray digit or symbol (e.g., "John2")	Passes through to Consolidated with no flag
Person Email	Value is literally "[none]"	Passes through, no flag
Person Email	Other format issues — malformed, or multiple emails combined in one field	Passes through, no flag
Person Date of Birth	Future-dated	Passes through, no flag
Person Tax ID	Garbage or placeholder values (e.g., 000000000, 123456789)	Passes through, no flag
Person Tax ID	Too short	Passes through, no flag


Not Checked At All
Column	Reason
Person ID Type	Informational field only — blank on ~96% of records even for confirmed valid Person records
System-generated/build-tool junk in name fields (e.g., "OutputFile," "CCDefines")	Confirmed real issue, but values too inconsistent to build one reliable rule. Documented as a known limitation.
