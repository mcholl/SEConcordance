from django.contrib import admin
from concordance.models import *

# Register your models here.
class VerseReferenceAdmin(admin.ModelAdmin):
	list_display = ['reference', 'get_sepost_title']

	def get_sepost_title(self, obj):
		return obj.sepost.posttitle
	get_sepost_title.short_description = 'in post titled'

class PostAdmin(admin.ModelAdmin):
	list_display = ['se_link', 'posttitle']

		

admin.site.register(SEPost, PostAdmin)
admin.site.register(VerseReference, VerseReferenceAdmin)