# Duplicate Report
- Total input rows: 79
- Duplicate candidates flagged: 18
- Name/phone format issues: 2

## Duplicate Details
- Alice Johnson (alice.johnson@email.com): duplicate email: alice.johnson@email.com also at row [2]; duplicate name+phone: row 2
- Bob Smith (bob.smith@email.com): duplicate email: bob.smith@email.com also at row [3]; duplicate name+phone: row 3
- anonymous_giraffe NeedsName (alice.johnson@email.com): duplicate email: alice.johnson@email.com also at row [2, 28]
- Evan Davis (evan.davis@email.com): duplicate email: evan.davis@email.com also at row [6]; duplicate name+phone: row 6
- Fiona Garcia (fiona.garcia@email.com): duplicate email: fiona.garcia@email.com also at row [7]; duplicate name+phone: row 7
- Kevin Anderson (kevin.a@email.com): duplicate name+phone: row 12
- Laura Thomas (laura.t@email.com): duplicate name+phone: row 13
- Mike Jackson (mike.jackson@email.com): duplicate email: mike.jackson@email.com also at row [14]; duplicate name+phone: row 14
- Nancy White (nancy.white@email.com): duplicate email: nancy.white@email.com also at row [15]; duplicate name+phone: row 15
- Patricia Clark (patricia.clark@email.com): duplicate email: patricia.clark@email.com also at row [17]
- Quinn Walker (qwalker@email.com): duplicate name+phone: row 18
- Tina Wright (tina.wright@email.com): duplicate email: tina.wright@email.com also at row [21]; duplicate name+phone: row 21
- Uma Scott (uma.scott@email.com): duplicate email: uma.scott@email.com also at row [22]; duplicate name+phone: row 22
- Victor Green (victor.green@email.com): duplicate email: victor.green@email.com also at row [23]; duplicate name+phone: row 23
- Wendy Baker (wendy.baker@email.com): duplicate email: wendy.baker@email.com also at row [24]; duplicate name+phone: row 24
- Xander Nelson (xander.nelson@email.com): duplicate email: xander.nelson@email.com also at row [25]; duplicate name+phone: row 25
- Yvonne Carter (yvonne.carter@email.com): duplicate email: yvonne.carter@email.com also at row [26]; duplicate name+phone: row 26
- Zachary Mitchell (zachary.mitchell@email.com): duplicate email: zachary.mitchell@email.com also at row [27]; duplicate name+phone: row 27

## Assumptions
- Email uniqueness is primary dedup signal
- Name+phone pair is secondary signal
- Phone normalized to (xxx) xxx-xxxx format
- Addresses capitalized but not geocoded
- Humorous placeholders: 'anonymous_giraffe', 'mystery_squid', 'NeedsName', 'NeedsSurname'

## What Could Be Wrong
- Some duplicates may be false positives (same name, different person)
- Phone normalization drops international codes
- Address normalization is cosmetic only