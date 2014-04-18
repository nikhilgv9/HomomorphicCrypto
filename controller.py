import cryptodao

def getAllRows():
	return cryptodao.getAllRows()

def getIdByRollNo(aRollNo):
	return cryptodao.getIdByRollNo(aRollNo)

def getRowById(aId):			
	return cryptodao.getRowById(aId)

def getTotal():
	return cryptodao.getTotal()

def updateStudentRecord(aRecord):
	return cryptodao.updateStudentRecord(aRecord)

def insertRecord(aRecord):
	return cryptodao.insertRecord(aRecord)

def deleteRecordById(aId):
	return cryptodao.deleteRecordById(aId)