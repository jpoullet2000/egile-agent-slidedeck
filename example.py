"""Example usage of the SlideDeck agent."""

import asyncio
import os
from dotenv import load_dotenv

from egile_agent_core import Agent
from egile_agent_core.models import XAI, OpenAI
from egile_agent_slidedeck import SlideDeckPlugin

load_dotenv()


async def main():
    """Demonstrate conversational deck creation."""
    print("\n" + "=" * 60)
    print("SLIDEDECK AGENT EXAMPLE")
    print("=" * 60 + "\n")
    
    # Create plugin (direct mode for this example)
    plugin = SlideDeckPlugin(use_mcp=False)
    
    # Select model
    if os.getenv("XAI_API_KEY"):
        model = XAI(model="grok-4-1-fast-reasoning")
        print("Using XAI (Grok) model")
    else:
        model = OpenAI(model="gpt-4o-mini")
        print("Using OpenAI model")
    
    # Create agent
    agent = Agent(
        name="slidedeck",
        model=model,
        plugins=[plugin],
        system_prompt=(
            "You are a professional presentation designer. "
            "Help users create compelling PowerPoint presentations."
        )
    )
    
    print("\nAgent created. Starting deck creation...\n")
    
    # Example conversation flow
    queries = [
        "Create a presentation about cloud security for CISOs",
        "Use 'ceo' audience and add a title slide about 'Securing the Cloud Era'",
        "Add a content slide about 'Zero Trust Architecture implementation'",
        "Add another slide about 'AI-powered threat detection reduces incidents by 60%'",
        "Export the deck as 'cloud_security.pptx'"
    ]
    
    for query in queries:
        print(f"User: {query}")
        print()
        
        response = await agent.process(query)
        print(f"Agent: {response}")
        print("\n" + "-" * 60 + "\n")
        
        # Small delay for readability
        await asyncio.sleep(1)
    
    print("=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
