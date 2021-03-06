import requests
import json

class BibleReference:
	"""Class that allows references to be sorted, compared, etc..."""

	plain_ref = ""   #Holds the textual representation (e.g. "1 Corinthians 13:4-7")

	book = ""
	book_num = 0
	end_book_num = 0
	start_chapter = 0
	start_verse = 0
	end_chapter = 0
	end_verse = 0

	biblia_apikey = "" #readini.get_ini_value('keys', 'biblia_apikey') to set

	def __init__(self):
		pass

	def __init__(self, verse_reference, api_key):
		self.biblia_apikey = api_key
		self.plain_ref = verse_reference
		self.parse()

	def is_valid(self):
		return (self.book_num > 0)

	def parse(self):
		#Use the Biblia API to parse the reference
		refparser_url = "http://api.biblia.com/v1/bible/parse"
		refparser_params = { "passage": self.plain_ref, "key": self.biblia_apikey}
		refparse = requests.get(refparser_url, params = refparser_params)

		if (refparse.status_code == 200):
			foundref = json.loads(refparse.text)
		else:
			print refparse.status_code
			raise Exception("Error parsing reference: {0} on {1}".format(refparse.status_code,refparse.url))

		try:
			parts = foundref['passages'][0]['parts']
		except:
			raise Exception('Unable to parse Reference: '+self.plain_ref)

		self.book = parts['book']
		self.start_chapter = parts['chapter'] if 'chapter' in parts else 0
		self.start_verse = parts['verse'] if 'verse' in parts else 0
		self.end_chapter = parts['endChapter'] if 'endChapter' in parts else self.start_chapter
		self.end_chapter = self.end_chapter if self.end_chapter > 0 else 1000

		self.end_verse = parts['endVerse'] if 'endVerse' in parts else self.start_verse
		self.end_verse = self.end_verse if self.end_verse > 0 else 1000

		#Set the Book Number
		the_book_name = self.book

		self.book_num = self.parse_book_num(the_book_name)
		self.end_book_num = self.parse_book_num(parts['endBook']) if 'endBook' in parts else self.book_num

		return

	def parse_book_num(self, book):

		all_books = [
			"Genesis",
			"Exodus",
			"Leviticus",
			"Numbers",
			"Deuteronomy",
			"Joshua",
			"Judges",
			"Ruth",
			"1 Samuel",
			"2 Samuel",
			"1 Kings",
			"2 Kings",
			"1 Chronicles",
			"2 Chronicles",
			"Ezra",
			"Nehemiah",
			"Esther",
			"Job",
			"Psalms",
			"Proverbs",
			"Ecclesiastes",
			"Song of Solomon",
			"Isaiah",
			"Jeremiah",
			"Lamentations",
			"Ezekiel",
			"Daniel",
			"Hosea",
			"Joel",
			"Amos",
			"Obadiah",
			"Jonah",
			"Micah",
			"Nahum",
			"Habakkuk",
			"Zephaniah",
			"Haggai",
			"Zechariah",
			"Malachi",
			"Tobit",
			"Judith",
			"Wisdom of Solomon",
			"Sirach",
			"Baruch",
			"1 Maccabees",
			"2 Maccabees",
			"1 Esdras",
			"2 Esdras",
			"3 Esdras",
			"4 Esdras",
			"3 Maccabees",
			"4 Maccabees",
			"Susanna",
			"Psalm 151",
			"Manasses",
			"Matthew",
			"Mark",
			"Luke",
			"John",
			"Acts",
			"Romans",
			"1 Corinthians",
			"2 Corinthians",
			"Galatians",
			"Ephesians",
			"Philippians",
			"Colossians",
			"1 Thessalonians",
			"2 Thessalonians",
			"1 Timothy",
			"2 Timothy",
			"Titus",
			"Philemon",
			"Hebrews",
			"James",
			"1 Peter",
			"2 Peter",
			"1 John",
			"2 John",
			"3 John",
			"Jude",
			"Revelation"]

		if book in all_books:
			return all_books.index(book)+1

		#TODO: If you are here, then the book is ambiguous.  Here, we need to make a best guess
		#Alternatively, we can lean on the Biblia API, because they've done the work to break everything else up
		#For now, return 0
		return 0


# #Tests
# refr = VerseReference("John 3:16")
# print vars(refr)
# refr = VerseReference("1 Corinthians 13:4-7")
# print vars(refr)
# refr = VerseReference("1 Corinthians 13:4-14:7")
# print vars(refr)
# refr = VerseReference("Jude 24-25")
# print vars(refr)
# refr = None
# try:
# 	refr = VerseReference("Jude 35")
# 	raise Exception("Bogus References should thrown an error!")
# except:
# 	pass
# refr = VerseReference("Hosea")
# print vars(refr)
