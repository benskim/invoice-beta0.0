# 📄 Invoice mismatch 

Input → Feature Extraction
      → Rule Layer (hard fail)
      → Score Layer (similarity)
      → Decision Layer (policy)
      → Output (Human check : accept / reject / review)
      
             ┌──────────────┐
             │ Dynamic Dict │  ← 계속 업데이트됨
             └──────┬───────┘
                    ↓
Input → Feature → Rule → Score → Decision
                             ↓
                        Feedback / LLM
                             ↓
                        Dict Update

[Step 1] Normalize
    - O→0, I→1
    - remove special char
    - standardize date

[Step 2] Hard Filter
    - invoice_no exact
    - vendor_id exact
    - currency exact
    - amount tolerance check

    → fail → mismatch

[Step 3] Line-level validation
    - qty * unit_price == total
    - item count consistency

    → fail → mismatch

[Step 4] Semantic similarity
    - desc embedding
    - address fuzzy

    → high score only match
    → else mismatch
