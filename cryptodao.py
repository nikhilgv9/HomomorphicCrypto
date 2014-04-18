#! /usr/bin/python
import MySQLdb as mysqldb
import serverproperties
import dberr
import columns
import record
import myerrors


QUERY_GET_ALL_ROWS = """select ID, ROLL_NO, MARK_1, WEIGHT_1, MARK_2, WEIGHT_2, TOTAL from student"""
QUERY_GET_ID_BY_ROLL = """select ID from student where ROLL_NO = """
QUERY_GET_ROW_BY_ID = """select ID, ROLL_NO, MARK_1, WEIGHT_1, MARK_2, WEIGHT_2, TOTAL from student where ID = """
QUERY_UPDATE_STUDENT_RECORD = """update student """
QUERY_INSERT_ROW = """insert into student(ROLL_NO, MARK_1, WEIGHT_1, MARK_2, WEIGHT_2, TOTAL) values ('%s', '%s', '%s', '%s', '%s', NULL)"""
QUERY_DELETE_ROW = """delete from student where ID = %s"""

class _dao(object):
	_instance = None

	class singleton:
		def __init__(self):
			try:
				self.connection = mysqldb.connect(serverproperties.LOCALHOST_ADDR, serverproperties.DB_USERNAME, serverproperties.DB_PASSWORD, serverproperties.DB_NAME)
			except:
				print "[Error]:"+dberr.DB_ERR_CONNECTING
				raise

	def __init__(self):
		if _dao._instance is None:
			_dao._instance = _dao.singleton()

	def __getattr__(self,aAttr):
		return getattr(_dao._instance,aAttr)

	def __setattr__(self, aAttr, aAttrValue):
		return setattr(_dao._instance, aAttr, aAttrValue)

def getCursor():
	return _dao().connection.cursor(mysqldb.cursors.DictCursor)

def _setDTO(aRow, aDTO):
	aDTO.setId(aRow[columns.ID])
	aDTO.setRollNo(aRow[columns.ROLL])
	aDTO.setMarks1(aRow[columns.MARK_1])
	aDTO.setMarks2(aRow[columns.MARK_2])
	aDTO.setWeight1(aRow[columns.WEIGHT_1])
	aDTO.setWeight2(aRow[columns.WEIGHT_2])
	aDTO.setTotal(aRow[columns.TOTAL])

def getAllRows():
	try:
		dtos = []
		cur = getCursor()
		cur.execute(QUERY_GET_ALL_ROWS)
		rows = cur.fetchall()

		for row in rows:
			dto = record.recordDTO()
			_setDTO(row, dto)
			dtos.append(dto)

		return dtos
	except:
		print "[Error]:"+dberr.DB_ERR_FETCHING_ROWS
		raise

def getIdByRollNo(aRollNo):
	try:
		myerrors.checkString(aRollNo)
		cur = getCursor()
		query = QUERY_GET_ID_BY_ROLL + mysqldb.escape_string(aRollNo)
		cur.execute(query)
		rows = cur.fetchall()
		if len(rows) == 0:
			return -1
		if len(rows) > 1:
			raise RuntimeException("[Error]:"+dberr.DB_ERR_MORE_THAN_ONE_ID_FOR_ROLL_NO)

		return rows[0][columns.ID]
	except:
		print "[Error]:"+dberr.DB_ERR_COULD_NOT_FETCH_ID_FROM_ROLL_NO
		raise

def getRowById(aId):		
	try:
		myerrors.checkInt(aId)
		cur = getCursor()		
		query = QUERY_GET_ROW_BY_ID + str(aId)
		cur.execute(query)
		rows = cur.fetchall()

		if len(rows) == 0:
			return record.recordDTO()

		if len(rows) > 1:
			raise RuntimeException("[Error]:"+dberr.DB_ERR_MORE_THAN_ONE_ROW_FOR_ID)

		dto = record.recordDTO()
		_setDTO(rows[0], dto)
		return dto

	except:
		print "[Error]:"+dberr.DB_ERR_COULD_NOT_FETCH_ROW_FROM_ID
		raise

def getTotal():
	pass

def updateStudentRecord(aRecord):
	try:
		myerrors.checkRecordForUpdate(aRecord)
		cur = getCursor()

		rollNo = mysqldb.escape_string(aRecord.getRollNo())
		marks1 = mysqldb.escape_string(aRecord.getMarks1())
		marks2 = mysqldb.escape_string(aRecord.getMarks2())
		weight1 = mysqldb.escape_string(aRecord.getWeight1())
		weight2 = mysqldb.escape_string(aRecord.getWeight2())
		total = mysqldb.escape_string(aRecord.getTotal() is None and "" or aRecord.getTotal())

		query = QUERY_UPDATE_STUDENT_RECORD \
		+ "set " + columns.ROLL + " = \'" + rollNo + "\', " \
		+ columns.MARK_1 + " = \'" + marks1 + "\', " \
		+ columns.MARK_2 + " = \'" + marks2 + "\', " \
		+ columns.WEIGHT_1 + " = \'" + weight1 + "\', " \
		+ columns.WEIGHT_2 + " = \'" + weight2 + "\'"
		if total.strip() == "":
			query = query + ", %s = NULL" % columns.TOTAL
		else:
			query = query + ", %s = '%s'" % (columns.TOTAL, total)

		query += " where ID = " + repr(int(aRecord.getId()))
		cur.execute(query)
		cur.connection.commit()

		return cur.rowcount

	except:
		print "[Error]:"+dberr.DB_ERR_COULD_NOT_UPDATE_RECORD
		raise

def insertRecord(aRecord):
	try:
		myerrors.checkRecordForInsert(aRecord)
		cur = getCursor()

		rollNo = mysqldb.escape_string(aRecord.getRollNo())
		marks1 = mysqldb.escape_string(aRecord.getMarks1())
		marks2 = mysqldb.escape_string(aRecord.getMarks2())
		weight1 = mysqldb.escape_string(aRecord.getWeight1())
		weight2 = mysqldb.escape_string(aRecord.getWeight2())
		total = mysqldb.escape_string(aRecord.getTotal() is None and "" or aRecord.getTotal())

		query = QUERY_INSERT_ROW % (rollNo, marks1, weight1, marks2, weight2)

		cur.execute(query)
		cur.connection.commit()

		return cur.rowcount
	except:
		print "[Error]:"+dberr.DB_ERR_COULD_NOT_INSERT_RECORD
		raise

def deleteRecordById(aId):
	try:
		myerrors.checkInt(aId)
		cur = getCursor()

		query = QUERY_DELETE_ROW % aId

		cur.execute(query)
		cur.connection.commit()

		return cur.rowcount
	except:
		print "[Error]:"+dberr.DB_ERR_COULD_NOT_DELETE_RECORD
		raise