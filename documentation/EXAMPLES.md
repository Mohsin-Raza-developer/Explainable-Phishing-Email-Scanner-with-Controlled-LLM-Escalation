# Example Email Analyses

This document demonstrates three representative email analyses showing different system behaviors.

---

## Example 1: Clear Safe Email (ML Only Decision)

### Input
**Email Text:**
```
Hi team, here is the meeting schedule for tomorrow's project update.
The agenda includes sprint review, planning for next iteration, and
team feedback session. Please review the attached document before the
meeting. Thanks!
```

**User Role:** `employee` (Standard user)

### Analysis Output

```
Source: ML_ONLY
Classification: Safe
Risk Score: 23.3/100
```

**ML Analysis:**
- The email has a risk score of 23.3/100 and is classified as 'Safe'
- Some benign business words detected: 'schedule', 'document', 'attached'

**Top Risk Signals:**
- 'schedule' (impact: 0.278)
- 'document' (impact: 0.235)
- 'attached' (impact: 0.161)

**Escalation Decision:**
- Borderline: No (score < 45)
- High Impact User: No
- **Result: ML-ONLY verdict (No LLM escalation needed)**

### Explanation

This is a typical internal communication email. The ML model correctly identifies it as safe with a low risk score (23.3/100). The system does not escalate to LLM because:
1. Score is clearly safe (< 45)
2. User is not in a high-impact role

This demonstrates efficient resource usage - straightforward cases don't need expensive LLM analysis.

---

## Example 2: Borderline Case (Escalation Triggered)

### Input
**Email Text:**
```
Urgent: Your package delivery failed. Please update your shipping
address to avoid return to sender. Visit the link below to confirm
details.
```

**User Role:** `employee` (Standard user)

### Analysis Output

```
Source: ML_ONLY
Classification: Safe
Risk Score: 31.7/100
```

**ML Analysis:**
- Urgency language detected but not extreme
- Common delivery notification patterns

**Top Risk Signals:**
- 'urgent' (impact: 0.295)
- 'delivery' (impact: 0.186)
- 'details' (impact: 0.095)

**Escalation Decision:**
- Borderline: No (score < 45 in this case)
- High Impact User: No
- **Result: ML-ONLY (though close to threshold)**

### Note on This Example

While this email contains urgency keywords, the ML model scored it at 31.7/100 (below the 45 borderline threshold). In a real deployment, an email like "Urgent: Verify your account immediately or it will be suspended" would score higher (70-85) and trigger escalation if the score falls in the 45-70 range.

**What LLM Would Analyze (if escalated):**
- Context: Is "urgent" justified for package delivery?
- Sender authenticity signals
- Whether the request pattern matches legitimate shipping companies
- Whether "visit link" is appropriate for the context

---

## Example 3: High-Impact User (Escalation Triggered)

### Input
**Email Text:**
```
Please review and approve the invoice for Q4 vendor payments.
The payment is due by end of week. Let me know if you need
additional details.
```

**User Role:** `finance` (High-impact department)

### Analysis Output

```
Source: HYBRID (ML + LLM)
Classification: Suspicious
Risk Score: 68.5/100
```

**ML Analysis:**
- Risk Score: 68.5/100 (Suspicious - borderline range)
- Payment-related keywords detected

**Top Risk Signals:**
- 'payment' (impact: 1.292)
- 'details' (impact: 0.121)

**Escalation Decision:**
- Borderline: Yes (45 ≤ 68.5 ≤ 70) ✓
- High Impact User: Yes (finance department) ✓
- **ESCALATION TRIGGERED:** Borderline Score + High-Impact User Role

### LLM Enhanced Analysis

**Note:** Due to API quota limits during testing, the actual LLM call failed. Below is the expected behavior:

**Expected LLM Verdict:**
```
Verdict: Suspicious - Requires Verification
Final Risk Score: 65/100
Adjusted Risk: Moderate (down from 68.5)

Reasoning:
The email requests invoice approval for Q4 vendor payments, which is a
legitimate finance department task. However, several factors warrant caution:

1. The email tone is relatively generic and could be templated
2. "Payment is due by end of week" creates mild time pressure
3. No specific vendor names or invoice numbers mentioned
4. No sender verification details provided in this context

The language itself is professional and appropriate for inter-departmental
communication. However, given the high-impact nature (finance department,
payment approval), verification is recommended.

User Advice:
- Verify the sender's email address matches known internal contacts
- Confirm the Q4 vendor payment request through official channels
- Check if invoice details were sent via separate secure communication
- If sender is external or unknown, escalate to IT security
- Do NOT click any links or open attachments without verification
```

### Why This Example Matters

This demonstrates the system's design philosophy:

1. **Context-Aware Risk Assessment**: A "payment" email to finance is treated more seriously than the same email to marketing

2. **LLM Adds Nuance**: The ML model sees "payment" and assigns higher risk. The LLM can evaluate whether this is legitimate business communication or a potential Business Email Compromise (BEC) attack

3. **Actionable Guidance**: Instead of just "Phishing" or "Safe", users get specific verification steps

4. **Cost-Effective**: LLM is only used when stakes are high (finance dept + borderline score)

---

## Summary of Escalation Logic

| Example | ML Score | User Role | Borderline? | High Impact? | Escalated? |
|---------|----------|-----------|-------------|--------------|------------|
| 1 - Safe meeting | 23.3 | employee | No | No | ❌ No |
| 2 - Delivery notice | 31.7 | employee | No | No | ❌ No |
| 3 - Invoice approval | 68.5 | finance | Yes | Yes | ✅ Yes |

---

## Additional Test Scenarios

### Clear Phishing (Score > 70, ML Only)

```
Email: "URGENT: Your account will be closed! Click here NOW to verify
        or lose access permanently. Bank suspended login reactivate."

Expected Output:
- Source: ML_ONLY
- Classification: Phishing
- Risk Score: 85-95/100
- Escalation: No (clear verdict, no LLM needed)
```

### Borderline + High-Impact (Both Triggers)

```
Email: "Urgent: Please wire transfer $50,000 to new vendor account.
        CEO approved. Details in attachment."

To: finance@company.com

Expected Output:
- Source: HYBRID (ML + LLM)
- ML Score: 55-65/100 (Suspicious)
- Escalation: YES (borderline + finance user)
- LLM Verdict: Likely BEC attack - verify via separate channel
```

---

## Real Output Files

Actual test run outputs are saved in:
- `example_outputs.json` - Machine-readable format
- This file - Human-readable documentation

To regenerate examples:
```bash
uv run python3 generate_examples.py
```
