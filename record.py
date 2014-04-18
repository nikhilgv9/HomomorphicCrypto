import columns

class recordDTO(object):
	def __init__(self, record=None):
		if record == None:
			self.m_id = -1
			self.m_rollNo = ""
			self.m_mark1 = ""
			self.m_weight1 = ""
			self.m_mark2 = ""
			self.m_weight2 = ""
			self.m_total = ""
		else:
			self.m_id = -1
			self.m_rollNo = record[columns.ROLL]
			self.m_mark1 = record[columns.MARK_1]
			self.m_weight1 = record[columns.WEIGHT_1]
			self.m_mark2 = record[columns.MARK_2]
			self.m_weight2 = record[columns.WEIGHT_2]
			self.m_total = ""

	def setId(self, aId):
		self.m_id = aId

	def getId(self):
		return self.m_id

	def setRollNo(self, aRollNo):
		self.m_rollNo = aRollNo

	def getRollNo(self):
		return self.m_rollNo

	def setMarks1(self, aMarks):
		self.m_mark1 = aMarks

	def getMarks1(self):
		return self.m_mark1

	def setWeight1(self, aWeight):
		self.m_weight1 = aWeight

	def getWeight1(self):
		return self.m_weight1

	def setMarks2(self, aMarks):
		self.m_mark2 = aMarks

	def getMarks2(self):
		return self.m_mark2

	def setWeight2(self, aWeight):
		self.m_weight2 = aWeight

	def getWeight2(self):
		return self.m_weight2

	def setTotal(self, aTotal):
		self.m_total = aTotal

	def getTotal(self):
		return self.m_total

	def __str__(self):
		dic = {}
		dic[columns.ID] = self.getId()
		dic[columns.ROLL] = self.getRollNo()
		dic[columns.MARK_1] = self.getMarks1()
		dic[columns.MARK_2] = self.getMarks2()
		dic[columns.WEIGHT_1] = self.getWeight1()
		dic[columns.WEIGHT_2] = self.getWeight2()
		dic[columns.TOTAL] = self.getTotal()

		return dic.__str__()

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		return hash(self.m_rollNo)

	def __eq__(self, aObj):
		isEq = True
		if aObj is None:
			return False

		if self is aObj:
			return True

		if not isinstance(aObj,recordDTO):
			return False

		else:
			that = aObj
			if this.getId() != that.getId():
				isEq = False
			
			elif this.getRollNo() != that.getRollNo():
				isEq = False

			elif this.getMarks1() != that.getMarks1():
				isEq = False				

			elif this.getWeight1() != that.getWeight1():
				isEq = False

			elif this.getMarks2() != that.getMarks2():
				isEq = False				

			elif this.getWeight2() != that.getWeight2():
				isEq = False

			elif this.getTotal() != that.getTotal():
				isEq = False

		return isEq

if __name__=="__main__":
	pass