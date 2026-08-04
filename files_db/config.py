Good catch — that's a mistake carried over from the wrong context. Hard/Soft was our Raw→Consolidated routing logic (whether a record gets excluded from Consolidated entirely or flagged-but-kept). Every record in this sheet has **already passed into Consolidated** — Silver isn't deciding include/exclude into a table anymore, it's about how to standardize the value itself, same as Mosaic's model: **Normalize / Exclude / N/A**.

Corrected — here's Email again without the Hard/Soft carryover:

## PERSON_EMAIL

| Value Pattern Description | Example | Record Count | Action | Normalization Logic | SQL Script |
|---|---|---|---|---|---|
| Perfect Valid Format | jayson.deleon@telusinternational.com | | N/A | — | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL LIKE '%_@_%.__%' AND PERSON_EMAIL NOT LIKE '%,%' AND PERSON_EMAIL NOT LIKE '%@%@%';` |
| `[none]` Placeholder | `[none]` | | Exclude | Not a real value — drop/blank it out in Silver | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL = '[none]';` |
| No @ Sign, Has Letters | johnsmith.com | | Exclude | Doesn't resemble an email — flag, don't guess-fix | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL IS NOT NULL AND LTRIM(RTRIM(PERSON_EMAIL)) <> '' AND PERSON_EMAIL NOT LIKE '%@%' AND PERSON_EMAIL LIKE '%[a-zA-Z]%';` |
| Multiple Emails (comma-separated) | john@x.com, jane@y.com | | Normalize | `email = email.split(',')[0].strip()` — or split into separate records | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL LIKE '%,%' AND PERSON_EMAIL LIKE '%@%';` |
| Has @ and Letters but Malformed | john@@x.com / john@ / @x.com | | Normalize | Strip repeated `@`, trailing/leading `@` | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL LIKE '%@%' AND (PERSON_EMAIL LIKE '%@%@%' OR PERSON_EMAIL LIKE '% %' OR PERSON_EMAIL LIKE '%@' OR PERSON_EMAIL LIKE '@%');` |
| No Letters At All | 12345@6789 | | Exclude | Not a real email value | `SELECT COUNT(*) FROM dbo.Bronze_PII_Table_Consolidated WHERE PERSON_EMAIL IS NOT NULL AND LTRIM(RTRIM(PERSON_EMAIL)) <> '' AND PERSON_EMAIL NOT LIKE '%[a-zA-Z]%';` |

Want me to redo DOB, Company Info, and Tax ID the same corrected way before you copy them in?
