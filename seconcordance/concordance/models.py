from django.db import models
from django.db import connection
from VerseReference import BibleReference
import re

# Create your models here.
class SEPost(models.Model):
	sepost = models.CharField(max_length=12, help_text="Stack Exchange Post Id", db_column="sepost_id", primary_key=True) 

	posttitle = models.CharField(max_length=255, help_text="Post Title (Always the title of the Question)", db_column="title", blank=True, null=True)
	se_link = models.URLField(max_length=255, help_text="link to the post on stack exchange", db_column="link", blank=True, null=True)
	body = models.TextField(default="", blank=True, null=True)

	score = models.IntegerField(help_text="Net of Up and Downvotes on post", db_column="score", blank=True, null=True) 
	owner = models.CharField(max_length=32, help_text="Display Name of the Post author", db_column="owner", blank=True, null=True)

	qa = models.CharField(max_length=1, help_text="Q for Question, A for Answer", db_column="type", blank=True, null=True)

	question_id = models.CharField(max_length=12, help_text="if you are an answer, this is the id of the parent question. if you are a question, link to yourself", blank=True, null=True)
	is_answered = models.NullBooleanField(help_text="True if this question has at least one answer", blank=True, null=True)
	is_closed = models.NullBooleanField(help_text="True if this question is on hold or otherwise not accepting new answers", blank=True, null=True)
	closed_reason = models.CharField(max_length=32, help_text="Reason for Closure", blank=True, null=True)

	@property
	def sitename(self):
		#Extracts the sitename from http://sitename.stackexchange.com/q/####
		p = re.compile(r'http://(?P<site>.+)\.stackexchange\.com')
		m = p.search(self.se_link)
		if m.groups('site'):
			return m.groups('site')[0]

		return "unknown"

	

class SETag(models.Model):
	id = models.AutoField(primary_key=True, db_column="reference_id")
	sepost = models.ForeignKey(SEPost)
	tag = models.CharField(max_length=255, help_text="tag")


class PassageManager(models.Manager):
	#Given something like VerseReference.in_range('Matthew - John'), this Manager returns a filtered queryset of VerseReferences in the specified range
	def in_range(self, filter_range):
		try:
			search_ref = BibleReference(filter_range)
		except Exception, e:
			raise Exception("Unable to parse search criteria '{0}'".format(filter_range))
			
		#return super(PassageManager, self).get_queryset().filter(book_num__gte=search_ref.book_num).filter(end_chapter__gte=search_ref.start_chapter).filter(end_verse__gte=search_ref.start_verse).filter(end_book_num__lte=search_ref.end_book_num).filter(start_chapter__lte=search_ref.end_chapter).filter(start_verse__lte=search_ref.end_verse)
		return super(PassageManager, self).get_queryset().filter(book_num__gte=search_ref.book_num,end_chapter__gte=search_ref.start_chapter,end_verse__gte=search_ref.start_verse,end_book_num__lte=search_ref.end_book_num,start_chapter__lte=search_ref.end_chapter,start_verse__lte=search_ref.end_verse)

class QuestionsManager(models.Manager):
	#Returns VerseRefrences on posted Questions Only
	def get_queryset(self):
		return super(QuestionsManager, self).get_queryset().filter(sepost__qa="q")

	#TODO: Really, this should be a mixin...
	def in_range(self, filter_range):
		search_ref = BibleReference(filter_range)
		if search_ref.plain_ref is None:
			raise Exception("Unable to parse search criteria '{0}'".format(filter_range))
		#return super(QuestionsManager, self).get_queryset().filter(book_num__gte=search_ref.book_num).filter(end_chapter__gte=search_ref.start_chapter).filter(end_verse__gte=search_ref.start_verse).filter(end_book_num__lte=search_ref.end_book_num).filter(start_chapter__lte=search_ref.end_chapter).filter(start_verse__lte=search_ref.end_verse)
		return super(PassageManager, self).get_queryset().filter(book_num__gte=search_ref.book_num,end_chapter__gte=search_ref.start_chapter,end_verse__gte=search_ref.start_verse,end_book_num__lte=search_ref.end_book_num,start_chapter__lte=search_ref.end_chapter,start_verse__lte=search_ref.end_verse)

class AnswersManager(models.Manager):
	#Returns VerseRefrences on posted Answers Only
	def get_queryset(self):
		return super(AnswersManager, self).get_queryset().filter(sepost__qa="a")

	#TODO: Really, this should be a mixin...
	def in_range(self, filter_range):
		search_ref = BibleReference(filter_range)
		if search_ref.plain_ref is None:
			raise Exception("Unable to parse search criteria '{0}'".format(filter_range))
		return super(AnswersManager, self).get_queryset().filter(book_num__gte=search_ref.book_num).filter(end_chapter__gte=search_ref.start_chapter).filter(end_verse__gte=search_ref.start_verse).filter(end_book_num__lte=search_ref.end_book_num).filter(start_chapter__lte=search_ref.end_chapter).filter(start_verse__lte=search_ref.end_verse)

class VerseReference(models.Model):	
	id = models.AutoField(primary_key=True, db_column="reference_id")
	sepost = models.ForeignKey('SEPost')

	reference = models.CharField(max_length=64, help_text="Plain text reference e.g. '1 Corinthians 13:4-7'", db_column="reference") 
	book_num = models.SmallIntegerField(help_text="Numerical position of canonical book, for sorting", db_column="ref_book_num") 
	end_book_num = models.SmallIntegerField(help_text="Numerical position of canonical book, for sorting", db_column="end_book_num")
	start_chapter = models.SmallIntegerField(help_text="Starting Chapter of the Reference", db_column="ref_startchapter_num")
	start_verse = models.SmallIntegerField(help_text="Starting verse", db_column="ref_startverse_num") 
	end_chapter = models.SmallIntegerField(help_text="End chapter", db_column="ref_endchapter_num") 
	end_verse = models.SmallIntegerField(help_text="End Verse", db_column="ref_endverse_num")
	start_index = models.SmallIntegerField(help_text="Position of the reference in the body of the post", db_column="se_post_index_start")
	length = models.SmallIntegerField(help_text="length of the reference in body of the post", db_column="se_post_reference_length")

	objects = models.Manager()
	answers = AnswersManager()
	questions = QuestionsManager()

	passages = PassageManager()

	@property
	def preview_snippet(self):
	 	return self.sepost.body[max(0,self.start_index-150): self.start_index + self.length + 150]

	class Meta:
		db_table="concordance_reference"
		ordering = ["book_num", "start_chapter", "start_verse", "end_book_num", "end_chapter", "end_verse"]


