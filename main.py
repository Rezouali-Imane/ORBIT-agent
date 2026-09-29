from langgraph.types import Command

from agent.manager import manager


def _review_interrupt(interrupts: list) -> dict:
       request = interrupts[0].value
       action = request["action_requests"][0]
       args = action["args"]
       print("\nProposed note")
       print(f"Title: {args.get('title', '')}")
       print(f"Content: {args.get('content', '')}")

       while True:
	       decision = input("Approve, edit, or reject? [a/e/r]: ").strip().lower()
	       if decision in {"a", "approve"}:
		       return {"decisions": [{"type": "approve"}]}
	       if decision in {"r", "reject"}:
		       reason = input("Reason (optional): ").strip()
		       result = {"type": "reject"}
		       if reason:
			       result["message"] = reason
		       return {"decisions": [result]}
	       if decision in {"e", "edit"}:
		       title = input(f"Title [{args.get('title', '')}]: ").strip()
		       content = input(f"Content [{args.get('content', '')}]: ").strip()
		       return {
			       "decisions": [
				       {
					       "type": "edit",
					       "edited_action": {
						       "name": "save_note",
						       "args": {
							       "title": title or args.get("title", ""),
							       "content": content or args.get("content", ""),
						       },
					       },
				       }
			       ]
		       }
	       print("Please choose approve, edit, or reject.")


def run_turn(question: str, thread_id: str) -> str:
       config = {"configurable": {"thread_id": thread_id}}
       result = manager.invoke(
	       {"messages": [{"role": "user", "content": question}]},
	       config=config,
       )
       while result.get("__interrupt__"):
	       result = manager.invoke(
		       Command(resume=_review_interrupt(result["__interrupt__"])),
		       config=config,
	       )
       return result["messages"][-1].content


def main() -> None:
	thread_id = input("Thread ID [orbit-default]: ").strip() or "orbit-default"
	print(f"ORBIT agent ready on thread '{thread_id}'. Type 'quit' to exit.")

	while True:
		question = input("\nYou: ").strip()
		if question.lower() in {"quit", "exit"}:
			break
		if not question:
			continue

		answer = run_turn(question, thread_id)

		print(f"\nAgent: {answer}")


if __name__ == "__main__":
	main()
