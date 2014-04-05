import re

#This class takes a snippet of Html and makes it safe for insertion into a page - intelligently balancing unbalanced tags and removing incomplete ones...

class TagBalancer:

	def __init__(self):
		pass

	def __init__(self, testString):
		self.parse(testString)

	def parse(self, testString):
		"""Analyzes the testString for potential tags"""

		self.testString = testString
		# print "==================================="
		# print testString
		# print "==================================="

		#Extract all potential < TAG GROUPS >, meaning anything that leads with a <.  
		#For ease of parsing, the regex will also get the tag name, or a closing tag 
		#(e.g. <SPAN, </SPAN, in addition to a naked <')

		find_tags = r'\<[\w+/[\w+]*]*'
		tag_name = r'(?<=\<)/?\w+'  #matches SPAN or /SPAN, intended to be in a tag group

		potential_tag_groups = re.findall(find_tags, testString)

		self.tag_groups = []
		nLeft = 0

		nOrder = 0
		for tag in potential_tag_groups:
			nOrder = nOrder + 1

			#Start some info about each potential tag
			tg = TagGroup()

			tg.name = ""
			tg.order = nOrder
			tg.tag_match = tag
			tg.is_self_closing = False
			tg.is_balanced = False
			tg.is_incomplete = False
			tg.is_closetag = False
			tg.pos = testString.find(tg.tag_match, nLeft+1)

			nLeft = tg.pos+1

			#Tags that don't have an ending angle bracket are unbalanced, end of story
			tg.endpos = testString.find(">", nLeft)
			if(tg.endpos == -1):
				tg.whole_tag = testString[tg.pos:]
				tg.is_incomplete = True
				self.tag_groups.append(tg)
				break

			#Set attributes
			tg.whole_tag = testString[tg.pos:tg.endpos+1]
			try:
				tg.name = re.findall(tag_name, tg.whole_tag)[0]
			except:
				pass

			tg.is_closetag =  tg.name.startswith('/')
			if tg.is_closetag:
				tg.name = tg.name[1:]

			#Self-Closing tags are Balanced
			if(tg.whole_tag.find("/>") > 0):
				tg.is_balanced = True
				tg.is_self_closing = True
				self.tag_groups.append(tg)
				break

			self.tag_groups.append(tg)

		#Make sure the list is in positional order
		self.tag_groups.sort(key=lambda x: x.pos)

		# #Question: When I updated the property, did it save?
		# for tag in self.tag_groups:
		# 	print "#{0}.{2} Name: {1}  from {3} to {4} ".format(tag.order, tag.name, tag.whole_tag, tag.pos, tag.endpos)
		# 	if tag.is_balanced:
		# 		print "		Is Balanced" 
		# 	if tag.is_closetag:	
		# 		print "		CLOSING tag"  
		# 	else:
		# 		print "     OPENING tag"

		#Check each complete but non-self-closing tag for a matchvafter the fact, 
		#and mark them as balanced 
		for tag in self.tag_groups:
			if tag.is_incomplete:
				break

			#If this is an open tag, Look for a close tag that comes after this positionally
			if not tag.is_closetag:
				close_tag = self.get_close_tag(tag)
				if close_tag is None:
					# print "{0} has no closing tag".format(tag.whole_tag)
					tag.is_balanced = False
				else:
					# print "{0} has a closing tag in {1}".format(tag.whole_tag, close_tag.whole_tag)
					close_tag.is_balanced = True
					tag.is_balanced = True
	
	def get_close_tag(self, open_tag):
		#Find the matching closing tag of tag.  note, i need to create a stack
		# print "Searching for a closing tag for {0}".format(open_tag.whole_tag)

		if open_tag.is_self_closing:
			# print "This tag closes itself!"
			return open_tag
		
		self.tag_groups.sort(key=lambda x: x.pos)
		n = 0

		#Ignore tags up to and including this tag
		while n < len(self.tag_groups):
			ignore_tag = self.tag_groups[n-1]
			if ignore_tag.pos == open_tag.pos:
				break

			n = n+1


		if n >= len(self.tag_groups):
			# print "Couldn't locate the position of the first tag!"
			return None

		#At this point, pot_tag == open_tag and n is the positional
		#Examine each of the remaining ones to see if it is the closing tag
		nested_tag_stack = []
		while n<len(self.tag_groups):
			next_tag = self.tag_groups[n]
			# print "     Could it be #{3}. {0} (at {1} to {2})?".format(next_tag.whole_tag, next_tag.pos, next_tag.endpos, n)

			if next_tag.name.strip().lower() == open_tag.name.strip().lower():
				# print "     the name matches at least"

				if next_tag.is_self_closing:
					# print "     Ignore the self closing tag"
					n = n+1
					continue

				if next_tag.is_closetag:
					if len(nested_tag_stack) == 0:
						# print "     found it!"
						return next_tag
					else:
						# print "     droping a nested tag of the same name"
						# print "			the stack now had {0} items".format(len(nested_tag_stack))
						nested_tag_stack.pop()
						# print "			the stack now has {0} items".format(len(nested_tag_stack))
				else:
					# print "     nested interior tag"
					nested_tag_stack.append(next_tag)
					# print "			the stack now has {0} items".format(len(nested_tag_stack))


			n = n+1

		#No matching closing tag was found
		return None

	def is_balanced(self):
		"""Returns True if every tag is balanced"""
		for tg in self.tag_groups:
			if not tg.is_balanced:
				return False

		return True

	def has_incomplete_tags(self):
		if len(self.tag_groups) > 0:
			last_tag = self.tag_groups[len(self.tag_groups)-1]
			return last_tag.is_incomplete

		return False

	def correct_snippet(self):
		if (self.is_balanced()):
			return self.testString

		retString = self.testString

		#Remove any incomplete tags from the string
		if self.has_incomplete_tags():
			# print "Stripping incomplete tag"
			# print " was =>{0}<=".format(retString)
			last_tag = self.tag_groups[len(self.tag_groups)-1]
			retString = retString[:last_tag.pos]
			last_tag.is_balanced = True
			# print " now =>{0}<=".format(retString)

		#Balance any unbalanced open tags
		for tag in reversed(self.tag_groups):
			if not tag.is_closetag:
				if not tag.is_balanced:
					# print "adding close tag for #{0}".format(tag.order)
					new_tag = "</{0}>".format(tag.name)
					retString += new_tag

		#Balance any unbalanced closing tags by prepending the string
		for tag in self.tag_groups:
			if tag.is_closetag:
				if not tag.is_balanced:
					# print "prepending open tag"
					new_tag = "<{0}>".format(tag.name)
					retString = new_tag + retString

		return retString

	def display_state(self):
		print "-------------------------------"
		for tag in self.tag_groups:
			self.display_tag(tag)

	def display_tag(self, tag):
		print "{0}. TAG = {1}".format(tag.order, tag.whole_tag)
		print "		name:{0}".format(tag.name)
		print "		position in string, from index {0} to {1}".format(tag.pos, tag.endpos)

		if tag.is_self_closing:
			print "		This is a self-closing tag"

		if tag.is_balanced:
			if tag.is_closetag:
				print "		This is a balanced closing tag of something else."
			else:
				close_tag = self.get_close_tag(tag)
				print "		This tag is closed by {0} at pos {1}".format(close_tag.whole_tag, close_tag.endpos)
		else:
			print "		WARNING: THIS TAG IS NOT BALANCED!!!!"

		if tag.is_incomplete:
			print "		WARNING: THIS TAG IS NOT COMPLETE!!!!"


class TagGroup:
	pass
			
def tests():
	s1 = "1. This is a string that has no tags."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = ">1b. This is a string that has no tags."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "2. This is a string that has <SPAN classs=''>Balanced Tags</SPAN> embedded"
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "3. This is a string that has two <SPAN classs=''>Balanced</SPAN> but separate <SPAN>Tags</SPAN> embedded"
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "4. This is a string that has a self closing tag <SPAN classs='' /> embedded"
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "5. This is a <SPAN class='1'>string that has <SPAN class='2'>nested spans</SPAN> in an unbalanced quote </SPAN>..."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "6. This is a <DIV class='1'>string that has <SPAN class='2'>nested spans</DIV> in an unbalanced quote </SPAN>..."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()

	s1 = "7. This is a <DIV class='1'>string that has <SPAN class='2'>nested spans</SPAN> in balance </DIV>..."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == True
	assert s1 == tb.correct_snippet()



	s1 = "8a. This is a string that has an <SPAN classs=''>open tag, but no closed one"
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == False
	assert s1+"</SPAN>" == tb.correct_snippet()
	print tb.correct_snippet()

	s1 = "8b. This is a <DIV class='1'>string that has <SPAN class='2'>nested spans<SPAN class='3'> and two of them aren't closed </SPAN>..."
	tb = TagBalancer(s1)
	# tb.display_state()
	assert tb.is_balanced() == False
	assert s1+"</SPAN></DIV>" == tb.correct_snippet()
	print tb.correct_snippet()

	s1 = "8c. This string has unclosed tags at the beginning</SPAN></DIV> is a <SPAN class='1'>string that has a nested closed</SPAN> making for an unbalanced quote ..."
	tb = TagBalancer(s1)
	assert tb.is_balanced() == False
	assert "<DIV><SPAN>"+s1 == tb.correct_snippet()



	s1 = "12. This is a string that has breaks in the middle of the <SPAN class=''>closing tag</SP"
	expected_result = s1+"AN>"
	tb = TagBalancer(s1)
	tb.display_state()
	assert tb.is_balanced() == False
	assert expected_result == tb.correct_snippet()



	s1 = "13. This is a string that has breaks in an unbalanced quote <SPAN class='"
	expected_result = "13. This is a string that has breaks in an unbalanced quote "
	tb = TagBalancer(s1)
	tb.display_state()
	assert tb.is_balanced() == False
	assert expected_result == tb.correct_snippet()


	#Failing Tests...

	s1 = "10. This is a string that has breaks in the middle of a <SPA"
	expected_result = "10. This is a string that has breaks in the middle of a "
	tb = TagBalancer(s1)
	tb.display_state()
	assert tb.is_balanced() == False
	print "=>{0}<=".format(tb.correct_snippet())
	print "=>{0}<=".format(expected_result)

	#These look the same, but aren't.  Why?
	# assert tb.correct_snippet() == expected_result

	s1 = "11. This is a string that has breaks at the begining of a tag <"
	expected_result = "11. This is a string that has breaks at the begining of a tag "
	tb = TagBalancer(s1)
	tb.display_state()
	assert tb.is_balanced() == False
	print "=>{0}<=".format(tb.correct_snippet())
	print "=>{0}<=".format(expected_result)
	# assert corrected == tb.correct_snippet()


	s1 = "9. This is a <SPAN class='1'>string that has a nested closed <SPAN /> in the middl of an otherwise balanced quote </SPAN>..."
	tb = TagBalancer(s1)
	tb.display_state()
	#assert tb.is_balanced() == True
	# print tb.correct_snippet()
	# assert s1 == tb.correct_snippet()

tests()
