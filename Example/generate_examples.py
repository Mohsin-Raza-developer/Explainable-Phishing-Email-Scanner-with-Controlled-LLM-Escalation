"""
Script to generate 3 example email analyses for documentation
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.append(str(Path(__file__).parent.parent))

from src.scanner import ScannerOrchestrator
import json

async def generate_examples():
    # Initialize scanner with pre-trained model
    scanner = ScannerOrchestrator(use_pretrained=True)

    # Test cases covering different scenarios
    test_cases = [
        {
            "name": "Example 1: Clear Safe Email (ML Only)",
            "email": "Hi team, here is the meeting schedule for tomorrow's project update. The agenda includes sprint review, planning for next iteration, and team feedback session. Please review the attached document before the meeting. Thanks!",
            "user_role": "employee",
            "description": "A legitimate internal communication with no suspicious indicators"
        },
        {
            "name": "Example 2: Borderline Suspicious (LLM Escalation)",
            "email": "Urgent: Your package delivery failed. Please update your shipping address to avoid return to sender. Visit the link below to confirm details.",
            "user_role": "employee",
            "description": "Contains urgency but could be legitimate - borderline score triggers LLM"
        },
        {
            "name": "Example 3: High-Impact User (LLM Escalation)",
            "email": "Please review and approve the invoice for Q4 vendor payments. The payment is due by end of week. Let me know if you need additional details.",
            "user_role": "finance",
            "description": "Legitimate-looking but sent to finance dept - high-impact trigger"
        }
    ]

    print("=" * 80)
    print("GENERATING EXAMPLE EMAIL ANALYSES")
    print("=" * 80)

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'=' * 80}")
        print(test['name'])
        print('=' * 80)
        print(f"Description: {test['description']}")
        print(f"User Role: {test['user_role']}")
        print(f"\nEmail Text:")
        print('-' * 80)
        print(test['email'])
        print('-' * 80)

        # Scan email
        result = await scanner.scan_email(test['email'], test['user_role'])

        # Display results
        print(f"\n{'=' * 80}")
        print("ANALYSIS RESULTS")
        print('=' * 80)
        print(f"Source: {result['source']}")
        print(f"Classification: {result['classification']}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"\nExplanation:")
        print(result['explanation'])

        if result.get('signals'):
            print(f"\nTop Risk Signals:")
            for sig in result['signals'][:5]:
                print(f"  - '{sig['word']}' (impact: {sig['impact']})")

        if 'llm_analysis' in result:
            print(f"\n{'*' * 80}")
            print("LLM ESCALATION ANALYSIS")
            print('*' * 80)
            llm = result['llm_analysis']
            print(f"Verdict: {llm.get('verdict', 'N/A')}")
            print(f"Final Risk Score: {llm.get('final_risk_score', 'N/A')}/100")
            print(f"\nReasoning:")
            print(llm.get('reasoning', 'N/A'))
            print(f"\nUser Advice:")
            print(llm.get('advice', 'N/A'))

        print(f"\n{'=' * 80}")

        # Store for JSON output
        results.append({
            'test_case': test['name'],
            'description': test['description'],
            'email': test['email'],
            'user_role': test['user_role'],
            'result': {
                'source': result['source'],
                'classification': result['classification'],
                'risk_score': result['risk_score'],
                'explanation': result['explanation'],
                'signals': result.get('signals', [])[:5],
                'llm_analysis': result.get('llm_analysis')
            }
        })

    # Save to JSON file
    with open('example_outputs.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'=' * 80}")
    print("Examples saved to example_outputs.json")
    print('=' * 80)

if __name__ == "__main__":
    asyncio.run(generate_examples())
