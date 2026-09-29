from agent.manager import manager


def main() -> None:
	print("ORBIT agent ready. Type 'quit' to exit.")

	while True:
		question = input("\nYou: ").strip()
		if question.lower() in {"quit", "exit"}:
			break
		if not question:
			continue

		result = manager.invoke({"messages": [{"role": "user", "content": question}]})
		answer = result["messages"][-1].content

		print(f"\nAgent: {answer}")


if __name__ == "__main__":
	main()
