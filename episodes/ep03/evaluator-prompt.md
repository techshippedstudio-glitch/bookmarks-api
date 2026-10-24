# Evaluator (S3, blind test of an artifact)

You are answering questions about a small bookmarks web API using only the material given to you. You have not seen the code, the build or any expected answers, and you must not look for them.

Material (read only this folder): <code>/specs/ (the branch's specs folder, exported with git archive)

Do not open any path outside that folder: not the code, not the other runs, and no git commands. Ignore any skill listings you may see; do not use them.

Questions:
1. What happens when I save a link I have already bookmarked? What status code comes back?
2. When I save a duplicate, is the existing bookmark's title or tags changed?
3. How does the API decide two links are the same link?
4. Which document is the current, authoritative description of save behavior?
5. How does the list endpoint page through results?

Rules:
- Answer each question only from the material. Quote the line that supports each answer, with file path and line number.
- If the material does not answer a question, or different files contradict each other, say exactly that and quote both sides. Do not guess and do not fill gaps from general knowledge.

Output: a markdown table with columns question, answer, supporting quote (file:line), confidence (high / low / not answerable). Then a short list of every contradiction you found between files, with quotes.