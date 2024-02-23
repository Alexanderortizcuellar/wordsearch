from wordsearch.wordsearch import WordSearch

words = ["apple", "mango", "grape"]
ws = WordSearch(words, 10, 10)
ws.generate()
ws.export_pdf("file.pdf", "my words")
ws.show(True)
