import dberr

def checkInt(aInt):
	if not isinstance(aInt,int) and not isinstance(aInt,long):
		print dberr.DB_ERR_INVALID_ID
		raise ValueError(dberr.DB_ERR_INVALID_ID)

	if aInt != int(aInt):
		print dberr.DB_ERR_INVALID_ID
		raise ValueError(dberr.DB_ERR_INVALID_ID)

def checkString(aString):
	if not isinstance(aString,str):
		raise ValueError(dberr.DB_ERR_INVALID_STRING)

	if aString.strip() is "":
		raise ValueError(dberr.DB_ERR_INVALID_STRING)

def checkRecordForUpdate(aRecord):
	checkInt(aRecord.getId())
	checkString(aRecord.getRollNo())
	checkString(aRecord.getMarks1())
	checkString(aRecord.getWeight1())
	checkString(aRecord.getMarks2())
	checkString(aRecord.getWeight2())

def checkRecordForInsert(aRecord):
	checkString(aRecord.getRollNo())
	checkString(aRecord.getMarks1())
	checkString(aRecord.getWeight1())
	checkString(aRecord.getMarks2())
	checkString(aRecord.getWeight2())

		
