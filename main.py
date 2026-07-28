import sys
import uuid
from langgraph.types import Command
from state.agent_state import create_initial_state
from graph.state_graph import assistant_graph

def print_banner():
    print("=" * 65)
    print(" 🤖 AI EXECUTIVE EMAIL & CALENDAR ASSISTANT (LangGraph)")
    print("=" * 65)
    print(" Built with LangGraph | OpenRouter Free Tier | HITL Protection")
    print(" Type 'exit' or 'quit' to end session.")
    print("=" * 65 + "\n")

def run_cli_session():
    print_banner()
    thread_id = f"cli_session_{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! 👋 Executive Assistant shutting down.")
                break

            print("\n⚙️  Processing request...")
            initial_state = create_initial_state(user_input)
            
            # 1. Run Graph Execution
            res = assistant_graph.invoke(initial_state, config=config)
            state_vals = assistant_graph.get_state(config).values

            # 2. Check if Human Approval is required
            if state_vals.get("approval_required") and state_vals.get("pending_action"):
                pending = state_vals["pending_action"]
                print("\n" + "⚠️ " * 15)
                print("HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
                print("⚠️ " * 15)
                print(f"Action Proposed: {pending.get('tool_name')}")
                print(f"Details: {pending.get('tool_args')}")
                print(f"Reason: {pending.get('reason')}")
                print("-" * 45)

                choice = input("\nDo you approve executing this action? (y/n): ").strip().lower()
                decision = "APPROVED" if choice in ["y", "yes"] else "REJECTED"

                print(f"\nSubmitting decision: {decision}...")
                res_final = assistant_graph.invoke(Command(resume={"approval_status": decision}), config=config)
                final_vals = assistant_graph.get_state(config).values
                print(f"\n🤖 Assistant: {final_vals.get('final_response')}")
            else:
                print(f"\n🤖 Assistant: {state_vals.get('final_response')}")

        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n❌ Error during execution: {str(e)}")

if __name__ == "__main__":
    run_cli_session()
