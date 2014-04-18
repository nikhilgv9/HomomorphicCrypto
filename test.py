#! /usr/bin/python

import controller
import record
if __name__ == "__main__":
	print "All Rows: ",controller.getAllRows(),"\n\n"
	print "ID for roll 321: ",controller.getIdByRollNo("321"),"\n\n"
	print "Row for ID 1: ",controller.getRowById(1),"\n\n"
	dto = record.recordDTO()
	dto.setId(1)
	dto.setRollNo('567')
	dto.setMarks1('456')
	dto.setMarks2('56')
	dto.setWeight1('6')
	dto.setWeight2('4')
	print "Rows Updated for ID 1: ",controller.updateStudentRecord(dto),"\n\n"

	dto.setRollNo('765')
	dto.setMarks1('92')
	dto.setWeight1('5')
	dto.setMarks2('45')
	dto.setWeight2('5')
	#print "Rows Inserted: ",controller.insertRecord(dto),"\n\n"

	print "Rows Deleted for ID 5: ",controller.deleteRecordById(3),"\n\n"



