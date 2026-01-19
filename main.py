from agent.runner import AgentRunner
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Stream live output to console")
    parser.add_argument("--interactive", action="store_true", help="Prompt interactively for queries")
    parser.add_argument("--query", default=None, help="Optional query to override default")
    args = parser.parse_args()

    runner = AgentRunner()
    if args.interactive:
        # Interactive loop: prompt the user for queries until they quit
        print("Entering interactive mode. Type 'q' or 'quit' to exit.")
        try:
            while True:
                q = input("Enter query (blank = default): ").strip()
                if q.lower() in ("q", "quit", "exit"):
                    print("Exiting interactive mode.")
                    break
                use_query = q if q else args.query
                runner.run_demo(query=use_query if use_query else None, live=args.live)
        except (KeyboardInterrupt, EOFError):
            print("\nInteractive session ended.")
    else:
        if args.live:
            runner.run_demo(query=args.query if args.query else None, live=True)
        else:
            runner.run_demo(query=args.query if args.query else None)


if __name__ == "__main__":
    main()
