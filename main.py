from agent.single_agent import agent


def main() -> None:
	print("ORBIT agent ready. Type 'quit' to exit.")

	while True:
		question = input("\nYou: ").strip()
		if question.lower() in {"quit", "exit"}:
			break
		if not question:
			continue

		result = agent.invoke({"messages": [{"role": "user", "content": question}]})
		messages = result["messages"]
		tool_names = [
			tool_call["name"]
			for message in messages
			for tool_call in getattr(message, "tool_calls", [])
		]
		answer = messages[-1].content

		print(f"\nAgent: {answer}")
		print(f"Tool called: {', '.join(tool_names) if tool_names else 'none'}")


if __name__ == "__main__":
	main()
