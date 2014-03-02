	 def __eq__(self, other):
	    return (self.book_num == other.book_num) and (self.start_chapter == other.start_chapter) and (self.start_verse == other.start_verse) and (self.end_chapter == other.end_chapter) and (self.end_verse == other.end_verse)


	 def __gt__(self, other):

	 	if (self.book_num > other.book_num):
	 		return True;
	 	else:
	 		if(self.book_num < other.book_num):
	 			return False

	 	if (self.start_chapter > other.start_chapter):
	 		return True;
	 	else:
	 		if(self.start_chapter < other.start_chapter):
	 			return False

	 	if (self.start_verse > other.start_verse):
	 		return True;
	 	else:
	 		if(self.start_verse < other.start_verse):
	 			return False

	 	if (self.end_chapter > other.end_chapter):
	 		return True;
	 	else:
	 		if(self.end_chapter < other.end_chapter):
	 			return False

	 	if (self.end_verse > other.end_verse):
	 		return True;
	 	else:
	 		if(self.end_verse < other.end_verse):
	 			return False

	 	return False


	 		objects = models.Manager()


class RefManager(models.Manager):
    def in_range(self, search_ref):
    	qry_in_range = "SELECT * FROM concordance_reference WHERE book_num=%s AND ref_endchapter_num >= %s AND ref_endverse_num >= %s AND ref_startchapter_num <= %s AND ref_startverse_num <= %s" 

        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(qry_in_range, (search_ref.book_num, search_ref.end_chapter, search_ref.end_verse, search_ref.start_chapter, search_ref.start_verse))
        result_list = []
        for row in cursor.fetchall():
            p = self.model()
            result_list.append(p)
        return result_list