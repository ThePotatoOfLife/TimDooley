# Rooted Bible Projection Implementation Plan

**Goal:** Attach existing reviewed public-X/Bible relations to Evidence Roots and candidate Episodes by stable references, without recomputing comparison meaning or changing source identity.

**Architecture:** Use each Root's `source_occurrence_ids` as the join key to existing Bible relation `occurrence_ids`. Emit compact Root→relation and Episode→inherited-relation indexes. Preserve relation ownership in the existing Bible files; unresolved occurrence references become explicit projection gaps.

**Constraints:**
- No quote/fuzzy matching for canonical joins.
- No new Bible comparison is created by this builder.
- Relation owners remain authoritative for verses, strength, source direction, counterpoints, and maximum claims.
- Episode inheritance means “one or more members have this relation,” not “the whole episode has this sequence-level relation.”
- Missing joins remain visible.
