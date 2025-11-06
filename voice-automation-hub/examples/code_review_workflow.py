"""Example: Code Review Workflow

This workflow demonstrates automated code review with multiple agents:
1. Research agent checks for similar patterns
2. Code agent analyzes code quality
3. Test agent validates test coverage
4. Analysis agent provides improvement recommendations
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from app.server import VoiceAutomationServer
from app.constants import OPENAI_API_KEY


async def main():
    """Run code review workflow example."""
    print("🔍 Starting Code Review Workflow...")
    print("=" * 60)

    # Initialize server
    server = VoiceAutomationServer(api_key=OPENAI_API_KEY)

    # Simulate code review request
    code_to_review = """
def calculate_discount(price, discount_percent):
    discount = price * discount_percent / 100
    final_price = price - discount
    return final_price

def process_order(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""

    print("\n📝 Code to review:")
    print(code_to_review)
    print("\n" + "=" * 60)

    # Create workflow
    task = f"""Review this Python code for quality, performance, and best practices:

{code_to_review}

Please:
1. Analyze code structure and style
2. Check for potential bugs or issues
3. Assess test coverage needs
4. Provide improvement recommendations
"""

    print("\n🤖 Creating automated code review workflow...")

    # In a real implementation, this would:
    # 1. Create workflow with orchestrator
    # 2. Spawn code agent for analysis
    # 3. Spawn test agent for coverage check
    # 4. Spawn analysis agent for recommendations
    # 5. Aggregate results

    print("\n✅ Workflow Steps:")
    print("  1. Code analysis (CodeAgent)")
    print("     - Style check: PEP 8 compliance")
    print("     - Complexity analysis")
    print("     - Security scan")
    print()
    print("  2. Test coverage check (TestAgent)")
    print("     - Missing test cases identified")
    print("     - Edge case analysis")
    print()
    print("  3. Recommendations (AnalysisAgent)")
    print("     - Type hints should be added")
    print("     - Use list comprehension in process_order")
    print("     - Add input validation")
    print()

    print("\n📊 Review Summary:")
    print("  - Issues found: 3 (2 medium, 1 low)")
    print("  - Test coverage: 0% (tests needed)")
    print("  - Complexity score: 4/10 (simple)")
    print("  - Security issues: None")
    print()

    print("\n💡 Top Recommendations:")
    print("  1. Add type hints: def calculate_discount(price: float, discount_percent: float) -> float")
    print("  2. Use sum() with generator: total = sum(item['price'] for item in items)")
    print("  3. Add input validation for discount_percent (0-100 range)")
    print("  4. Add docstrings to functions")
    print("  5. Create unit tests with pytest")
    print()

    print("\n" + "=" * 60)
    print("✨ Code review complete!")


if __name__ == "__main__":
    asyncio.run(main())

