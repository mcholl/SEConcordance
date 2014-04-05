import re
import pprint
#Test a function to balance tags


class TagBalancer:

	def __init__(self):
		pass

	def __init__(self, testString):
		self.parse(testString)

	def parse(self, testString):
		"""Analyzes the testString for potential tags"""

		self.testString = testString
		print "==================================="
		print testString
		print "==================================="

		#Extract all potential < TAG GROUPS >, meaning anything that leads with a <.  
		#For ease of parsing, the regex will also get the tag name, or a closing tag 
		#(e.g. <SPAN, </SPAN, in addition to a naked <')

		find_tags = r'\<[\w+/[\w+]*]*'
		tag_name = r'(?<=\<)/?\w+'  #matches SPAN or /SPAN, intended to be in a tag group

		potential_tag_groups = re.findall(find_tags, testString)

		self.tag_groups = []
		nLeft = 0

		for tag in potential_tag_groups:
			#Start some info about each potential tag
			tg = TagGroup()

			tg.name = ""
			tg.tag_match = tag
			tg.is_self_closing = False
			tg.is_balanced = False
			tg.is_incomplete = False
			tg.pos = testString.find(tg.tag_match, nLeft)

			nLeft = tg.pos

			#Tags that don't have an ending angle bracket are unbalanced, end of story
			tg.endpos = testString.find(">", nLeft)
			if(tg.endpos == -1):
				tg.whole_tag = testString[tg.pos:]
				tg.is_incomplete = True
				self.tag_groups.append(tg)
				break

			#Set attributes
			tg.whole_tag = testString[tg.pos:tg.endpos+1]
			tg.name = re.findall(tag_name, tg.whole_tag)[0]

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

		#Check each complete but non-self-closing tag for a matchvafter the fact, 
		#and mark them as balanced 
		for tag in self.tag_groups:
			if tag.is_incomplete:
				break

			#If this is an open tag, Look for a close tag that comes after this positionally
			if not tag.is_closetag:
				close_tag = self.get_close_tag(tag)
				if close_tag is None:
					print "{0} has no closing tag".format(tag.whole_tag)
					tag.is_balanced = False
				else:
					print "{0} has a closing tag in {1}".format(tag.whole_tag, close_tag.whole_tag)
					close_tag.is_balanced = True
					tag.is_balanced = True

		#Question: When I updated the property, did it save?
		self.tag_groups.sort(key=lambda x: x.pos)
		for tag in self.tag_groups:
			print "Pos: {0} Name: {1}  tag: {2}".format(tag.pos, tag.name, tag.whole_tag)
	
	def get_close_tag(self, open_tag):
		#Find the matching closing tag of tag.  note, i need to create a stack
		print "Searching for a closing tag for {0}".format(open_tag.whole_tag)
		
		self.tag_groups.sort(key=lambda x: x.pos)
		n = 0

		#Ignore tags up to and including this tag
		while n < len(self.tag_groups):
			ignore_tag = self.tag_groups[n-1]
			if ignore_tag.pos == open_tag.pos:
				break
			n = n+1
		if n == len(self.tag_groups):
			print "Couldn't locate the position of the first tag!"
			return None


		#At this point, pot_tag == open_tag and n is the positional
		#Examine each of the 
		print "Looking beyond position {0}".format(n)
		nested_tag_stack = []
		while n<=len(self.tag_groups):
			next_tag = self.tag_groups[n]
			print "     Could it be {0}?".format(next_tag.whole_tag)
			if next_tag.name.strip().lower() == open_tag.name.strip().lower():
				print "     the name matches at least"
				if next_tag.is_self_closing:
					print "     Ignore the self closing tag"
					continue

				if next_tag.is_closetag:
					if nested_tag_stack == []:
						print "     found it!"
						return next_tag
					else:
						print "     droping a nested tag of the same name"
						nested_tag_stack.pop()

				print "     nested interior tag"
				nested_tag_stack.append(next_tag)
			n = n+1

		#No matching closing tag was found
		return None

	def is_balanced(self):
		"""Returns True if every tag is balanced"""
		for tg in self.tag_groups:
			if not tg.is_balanced:
				return False

		return True

	def correct_snippet(self):
		if (self.is_balanced()):
			return self.testString

		print "Need to balance out unbalanced tags!"
		return None

	def display_state(self):
		for tag in self.tag_groups:
			self.display_tag(tag)

	def display_tag(self, tag):
		print "{0}".format(tag.whole_tag)
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


class TagGroup:
	pass
			

s1 = "1. This is a string that has no tags."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = ">1b. This is a string that has no tags."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "2. This is a string that has <SPAN classs=''>Balanced Tags</SPAN> embedded"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "3. This is a string that has two <SPAN classs=''>Balanced</SPAN> but separate <SPAN>Tags</SPAN> embedded"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "4. This is a string that has a self closing tag <SPAN classs='' /> embedded"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "5. This is a string that has an <SPAN classs=''>open tag, but no closed one"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == False
assert s1+"</SPAN>" == tb.correct_snippet()

s1 = "6. This is a string that has breaks in the middle of a <SPA"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == False
assert s1+" />" == tb.correct_snippet()

s1 = "7. This is a string that has breaks at the begining of a tag <"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == False
assert s1+" />" == tb.correct_snippet()

s1 = "8. This is a string that has breaks in the middle of the <SPAN class=''>closing tag</SP"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == False
assert s1+"AN>" == tb.correct_snippet()

s1 = "9. This is a string that has breaks in an unbalanced quote <SPAN class='"
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == False
assert s1+"' />" == tb.correct_snippet()


s1 = "10. This is a <SPAN class='1'>string that has <SPAN class='2'>nested spans</SPAN> in an unbalanced quote </SPAN>..."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "11. This is a <SPAN class='1'>string that has a nested closed<SPAN /> in an unbalanced quote </SPAN>..."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()


s1 = "12. This is a <DIV class='1'>string that has <SPAN class='2'>nested spans</DIV> in an unbalanced quote </SPAN>..."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()

s1 = "13. This is a <DIV class='1'>string that has <SPAN class='2'>nested spans</SPAN> in an unbalanced quote </DIV>..."
tb = TagBalancer(s1)
tb.display_state()
assert tb.is_balanced() == True
assert s1 == tb.correct_snippet()