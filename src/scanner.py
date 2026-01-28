import asyncio
from .ml_classifier import PhishingClassifier
from . import llm_agent

class ScannerOrchestrator:
    def __init__(self, use_pretrained=True, model_path='phishing_model.pkl'):
        print("Initializing Scanner Orchestrator...")
        self.ml_model = PhishingClassifier()

        # Try to load pre-trained model, otherwise train new one
        if use_pretrained and self.ml_model.load_model(model_path):
            print("Using pre-trained model.")
        else:
            print("Training new model on CEAS_08.csv dataset...")
            print("(This will take a few minutes with 39K+ emails)")
            self.ml_model.train()
            self.ml_model.save_model(model_path)
            print(f"Model trained and saved to {model_path}")
        
    async def scan_email(self, email_text, user_role="employee"):
        """
        Scans an email using ML, and escalates to LLM if necessary.
        
        Escalation Triggers:
        1. Score is Borderline (45 - 70)
        2. User Role is High-Impact ('finance', 'hr', 'executive')
        """
        print(f"\n--- Scanning Email for User: {user_role} ---")
        print(f"Text Preview: '{email_text[:40]}...'")
        
        # Step 1: Fast ML Check (Synchronous)
        ml_result = self.ml_model.analyze_email(email_text)
        risk_score = ml_result['risk_score'] # Extract score (0-100) from ML result to decide if LLM is needed 
        
        print(f"ML Result: Score {risk_score}/100 | Class: {ml_result['classification']}")
        
        # Step 2: Check Escalation Triggers
        # Condition A: Borderline Score,  compareson oprator
        is_borderline = 45 <= risk_score <= 70
        # print(f"Borderline: {is_borderline}, bool")
        
        # Condition B: High Impact User
        high_impact_roles = ['finance', 'hr', 'executive']
        is_high_impact = user_role.lower() in high_impact_roles
        # print(f"High Impact: {is_high_impact}, bool")
        
        should_escalate = is_borderline or is_high_impact
        # print(f"Should Escalate: {should_escalate}, bool")
        
        final_verdict = {
            "source": "ML_ONLY",
            "risk_score": risk_score,
            "classification": ml_result['classification'],
            "explanation": ml_result['explanation'],
            "signals": ml_result['ml_signals']
        }

        # Step 3: Execute Logic
        if should_escalate:
            trigger_reason = []
            if is_borderline: trigger_reason.append("Borderline Score")
            if is_high_impact: trigger_reason.append(f"High-Impact User Role  {user_role}")
            
            print(f">> ESCALATION TRIGGERED: {', '.join(trigger_reason)}")
            print(">> Calling LLM Agent... (Please wait)")
            
            # Call Async LLM Agent
            llm_result = await llm_agent.analyze_with_llm(email_text, ml_result)
            
            # Merge Results
            final_verdict["source"] = "HYBRID (ML + LLM)"
            final_verdict["llm_analysis"] = llm_result
            final_verdict["classification"] = llm_result.get('verdict', ml_result['classification'])
            final_verdict["explanation"] = llm_result.get('reasoning', "LLM provided no reasoning.")
            final_verdict["advice"] = llm_result.get('advice', "Proceed with caution.")
            final_verdict["final_score"] = llm_result.get('final_risk_score', risk_score)
            
        return final_verdict
