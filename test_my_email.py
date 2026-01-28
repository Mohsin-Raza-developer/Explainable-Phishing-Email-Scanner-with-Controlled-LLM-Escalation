import asyncio
from src.scanner import ScannerOrchestrator

async def test():
    
    scanner = ScannerOrchestrator(use_pretrained=True)

    my_email = """
    Subject: Invoice for Q4 Vendor Payments

    Hi Team,

Please find attached the invoice for Q4 vendor payments. The payment is due by end of week. Let me know if you need additional details.

Thanks,
Finance Dept
    """

    
    user_role = "Finance"
    

    # Analyze
    print("\n" + "="*60)
    print("ANALYZING EMAIL...")
    print("="*60)

    result = await scanner.scan_email(my_email, user_role)

# Run
asyncio.run(test())
