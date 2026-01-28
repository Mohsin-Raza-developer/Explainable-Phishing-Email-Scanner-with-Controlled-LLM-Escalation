from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is present
if not api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables. LLM calls will fail.")


# enable_verbose_stdout_logging()
    

external_client = AsyncOpenAI(
        api_key = api_key,
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
    )


model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

config = RunConfig(
    model= model,
    tracing_disabled=True,

)


# Define Structured Output Schema
class PhishingVerdict(BaseModel):
    verdict: str = Field(description="The final classification: 'Safe', 'Suspicious', or 'Phishing'")
    reasoning: str = Field(description="A clear explanation of why this decision was made.")
    advice: str = Field(description="Actionable advice for the user (e.g., 'Delete email', 'Contact sender').")
    final_risk_score: float = Field(description="Adjusted risk score (0-100) based on analysis.")

# Define the Agent's Persona and Instructions
phishing_analyst = Agent(
    name='SecurityAnalyst',
    instructions="""You are an expert Security Analyst. Your job is to analyze suspicious emails.
    
    You will receive:
    1. The email text.
    2. A risk score and signals from a Machine Learning model.
    
    Your goal is to provide a FINAL VERDICT based on both the text and the ML signals.
    
    RULES:
    1. Do NOT blindly override the ML Score. If the ML detected high-risk keywords (like 'Urgent', 'Bank'), take them seriously.
    2. However, if the email context makes sense (e.g., 'Urgent meeting about lunch' vs 'Urgent bank transfer'), you can downgrade the risk.
    """,
    output_type=PhishingVerdict # Enforce structured output
)

async def analyze_with_llm(email_text, ml_result):
    """
    Analyzes the email using the LLM agent with structured output.
    """
    if not api_key:
        return {
            "verdict": "Error",
            "reasoning": "LLM API Key missing. Could not perform advanced analysis.",
            "advice": "Check system configuration.",
            "final_risk_score": ml_result['risk_score']
        }

    # Prepare the input for the agent
    prompt = f"""
    Analyze this email:
    ---
    {email_text}
    ---
    
    ML Model Output:
    - Risk Score: {ml_result['risk_score']}/100
    - Classification: {ml_result['classification']}
    - Identified Signals: {ml_result.get('ml_signals', [])}
    
    
    Provide your structured analysis.
    """
    
    try:
        # Run the agent
        result = await Runner.run(phishing_analyst, prompt, run_config=config)
        
        # The result.final_output_as(type) helper isn't always available in all versions, 
        # but result.final_output will be an instance of PhishingVerdict because output_type was set.
        verdict_obj = result.final_output
        
        # return as dict for compatibility with scanner.py
        return verdict_obj.model_dump()
        
    except Exception as e:
        print(f"LLM Analysis Failed: {e}")
        return {
            "verdict": "Error",
            "reasoning": "LLM Analysis encountered an error.",
            "advice": "Rely on ML verdict.",
            "final_risk_score": ml_result['risk_score']
        }


