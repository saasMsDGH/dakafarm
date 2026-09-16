with open("C:/Users/user/.gemini/antigravity/brain/26d6b07e-043e-479e-9594-767fd9ef5897/task.md", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("- [ ]", "- [x]")

with open("C:/Users/user/.gemini/antigravity/brain/26d6b07e-043e-479e-9594-767fd9ef5897/task.md", "w", encoding="utf-8") as f:
    f.write(text)
