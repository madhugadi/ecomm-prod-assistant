PERSON_EMAIL
Value Pattern Description	Example	Record Count	Action	Normalization Logic
Perfect Valid Format	jayson.deleon@telusinternational.com	(Albiona fills)	N/A	—
[none] Placeholder	[none]		Exclude / Hard	Flag as missing, treat as junk
No @ Sign, Has Letters	johnsmith.com		Exclude / Hard	Not attempting email shape
Multiple Emails (comma-separated)	john@x.com, jane@y.com		Normalize / Soft	Split into individual values or flag first as primary
Has @ and Letters but Malformed	john@@x.com, john@		Normalize / Soft	Structural repair where possible
No Letters At All	12345@6789		Exclude / Hard	Safeguard rule — 0 records hit this in Raw, confirm in Consolidated
PERSON_DATE_OF_BIRTH
Value Pattern Description	Example	Record Count	Action	Normalization Logic
Valid Range	1985-04-12		N/A	—
Pre-1900 (placeholder pattern)	1899-12-30		Exclude / Hard	Confirmed systemic placeholder — verify still true in Consolidated
Future Date	2046-04-09		Normalize / Soft	Verify against other fields — may be real person with typo year
Company Info in Name Fields (First/Middle/Last/Full)
Value Pattern Description	Example	Record Count	Action	Normalization Logic
Company Keyword Match	FSC LA PALOMA ASSOCIATES LLC		Exclude or Route / Hard	Move out of Person name fields — check RECORD_TYPE
Digit-Prefix / Store Number	STORAGE USA #703		Exclude or Route / Hard	Same as above
& Symbol Present	T & C MANAGEMENT		Exclude or Route / Hard	Same as above
Keyword list to test	LLC, INC, CORP, LTD, DBA, GROUP, ENTERPRISE, PARTNERS, PARTNERSHIP, ASSOCIATES, DISTRICT, SCHOOL, DEPARTMENT
