from django.db import models

# Create your models here.
class SEPost(models.Model):
	sepost = models.CharField(max_length=12, help_text="Stack Exchange Post Id", db_column="sepost_id", primary_key=True) 
	owner = models.CharField(max_length=32, help_text="Display Name of the Post author", db_column="owner")
	qa = models.CharField(max_length=1, help_text="Q for Question, A for Answer", db_column="type")
	posttitle = models.CharField(max_length=255, help_text="Post Title (Always the title of the Question)", db_column="title")
	se_link = models.URLField(max_length=255, help_text="link to the post on stack exchange", db_column="link")
	score = models.IntegerField(help_text="Net of Up and Downvotes on post", db_column="score") 
	body = models.TextField()

class VerseReference(models.Model):	
	id = models.AutoField(primary_key=True, db_column="reference_id")
	sepost = models.ForeignKey('SEPost')

	#sepost = models.CharField(max_length=12, help_text="Key to the Stack Exchange Post", db_column="sepost_id")
	reference = models.CharField(max_length=64, help_text="Plain text reference e.g. '1 Corinthians 13:4-7'", db_column="reference") 
	book_num = models.SmallIntegerField(help_text="Numerical position of canonical book, for sorting", db_column="ref_book_num") 
	start_chapter = models.SmallIntegerField(help_text="Starting Chapter of the Reference", db_column="ref_startchapter_num")
	start_verse = models.SmallIntegerField(help_text="Starting verse", db_column="ref_startverse_num") 
	end_chapter = models.SmallIntegerField(help_text="End chapter", db_column="ref_endchapter_num") 
	end_verse = models.SmallIntegerField(help_text="End Verse", db_column="ref_endverse_num")
	start_index = models.SmallIntegerField(help_text="Position of the reference in the body of the post", db_column="se_post_index_start")
	length = models.SmallIntegerField(help_text="length of the reference in body of the post", db_column="se_post_reference_length")

	@property
	def preview_snippet(self):
	 	return self.sepost.body[max(0,self.start_index-150): self.start_index + self.length + 150]

	class Meta:
		db_table="concordance_reference"
		ordering = ["book_num", "start_chapter", "start_verse"]
		