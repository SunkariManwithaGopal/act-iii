# Agent Rules

Rules for all teammates' AI agents working on Restock Copilot:

- Edit only files in your own folder.
- Never change docs/contracts/.
- Never commit .env, keys, data files or model files.
- Run pytest before saying a task is done.
- Add no new libraries without asking.
- Keep each change small and explain it in 3 lines.
- For any ML code: never use a random split; training dates must be earlier than test dates; add a test for it.
- Never invent numbers; every number in docs must come from a file in eval/.
- Ask before running terminal commands, git push, or anything that deletes files.
