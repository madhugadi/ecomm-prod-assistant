Final Rule Set — Fully Verified
Column	Check	Severity Logic
First/Middle/Last Name	Letters (any script) vs. digits/symbols	Skip if NULL. Hard if no letters at all OR digits ≥50% of string. Soft if letters dominant with minor digit/symbol. Clean otherwise.
Email	Format validity	[none] → Hard. Other format failures → Soft. NULL allowed.
Date of Birth	Plausibility range	Pre-1900 → Hard (confirmed empty placeholder records). Future date → Soft (confirmed real people, just bad date). NULL allowed.
Tax ID	Garbage/placeholder detection	Placeholder/non-alphanumeric → Hard. Too-short-but-alphanumeric → Soft. NULL allowed.
Address	Symbols / corruption	Hex-garbage (0x...) → Hard (confirmed empty records, nothing salvageable). Other symbols → Soft. NULL allowed.
Company Info (ET1)	Business keywords	Always Hard
Digit-Prefixed Name (ET2)	Starts with digit	Always Hard
Person_ID_Type	—	Not checked
Person_ID → Tax_ID	SSN misplaced	Correction, not a check
Routing
Clean → Consolidated only
Soft → Consolidated + Errors
Hard → Errors only
