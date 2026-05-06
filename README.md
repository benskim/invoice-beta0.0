# 📄 Invoice mismatch 

1. Upload / Input
2. Parsing (OCR + parser / LLM 보조)
3. Feature Extraction (+ normalization, dict)

4. Candidate Generation (line match, Top-K)

5. Validation Core
   5-1. Rule Layer (hard fail / hard pass)
   5-2. Score Layer (soft similarity)

6. Decision Layer (policy)
   - hard fail → REJECT
   - hard pass + very high score → AUTO ACCEPT (unique)
   - no good candidate → AUTO REJECT
   - else → REVIEW (selection basket)

7. Explanation Layer
   7-1. Reason Generator (rule/score 근거를 구조적으로 출력)
   7-2. Action Recommendation (accept / reject 가이드)

8. UI (Focus / Basket / Diff View)

9. Feedback (user correction / confirmation)

10. Learning Loop
   - dict update
   - rule tuning
   - weight/threshold tuning
      
-----------simple steps----------- 

[Step 1] Normalize
    - O→0, I→1
    - remove special char
    - standardize date

[Step 2] Line-level validation
    - qty * unit_price == total
    - item count consistency

    → fail → mismatch

[Step 3] Hard Filter
    - invoice_no exact
    - vendor_id exact
    - currency exact
    - amount tolerance check

    → fail → mismatch

[Step 4] Semantic similarity
    - desc embedding
    - address fuzzy

    → high score only match
    → else mismatch
-----------

* mismatch cases in a taxonomy excel file
