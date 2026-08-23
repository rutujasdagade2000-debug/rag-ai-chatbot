knowledge ={}

files = ('ai_news.txt', 'companies.txt', 'models.txt')
for filename in files:
    file=  open(filename, "r", encoding= "utf-8")
    for line in file:
        question, answer = line.strip().split(":", 1)
        knowledge[question.lower()]= answer.strip()
file.close()
while True:
    user = input("You: ").lower()
    if user == "exit":
        print("Bot: Goodbye!")
        break
    found= False
    for question in knowledge:
        if user in question or question in user:
            print("Bot:", knowledge[question])
            found= True
            break
    if not found:
        print("Bot: Sorry, I do not know the answer.")