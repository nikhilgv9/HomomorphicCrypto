import socket
import sys
import clientproperties
import FHC
import columns
import ast
import time

def showMenu():
	print "\n".join(clientproperties.CLIENT_MENU),

class myclient:
	def __init__(self,aAddr,aPortNo):
		self.m_servAddr = (aAddr,aPortNo)
		self.m_die = False
		self.m_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	def connect(self):
		try:
			self.m_sock.connect(self.m_servAddr)
			print "[%s] %s %s" % (clientproperties._getTime(),clientproperties.CLIENT_CONNECTED_MSG,self.m_servAddr)
			self.start()
		except:
			print "[%s] %s %s" % (clientproperties._getTime(),clientproperties.CLIENT_CANNOT_CONNECT_MSG,self.m_servAddr)
			self._cleanUp()
			sys.exit(2)

	def _recv(self):
		buff = self.m_sock.recv(clientproperties.CLIENT_MAX_RECV)
		done = False
		while not done:
			if '\n' in buff:
				(line,buff) = buff.split('\n',1)	#split on \n, max 1 split
				return line+'\n'
			else:
				more = self.m_sock.recv(clientproperties.CLIENT_MAX_RECV)
				if not more:
					done = True
				else:
					buff += more

		if buff:
			return buff

	def start(self):
		while not self.m_die:			
			msg = self._recv()			
			self._checkQuit(msg)
			print "[%s] %s: %s" % (clientproperties._getTime(),clientproperties.SERVER,msg)

			#display menu
			if not self.m_die:
				showMenu()
				self._handleInput()

	def _checkQuit(self,msg):
		if msg.strip() == clientproperties.CLIENT_SERVER_QUIT_MSG:
			print "[%s] %s" % (clientproperties._getTime(),clientproperties.CLIENT_QUIT_REQUEST_MSG)	
			self._cleanUp()

	def _cleanUp(self):
		print "[%s] %s" % (clientproperties._getTime(),clientproperties.CLIENT_CLEANUP_MSG)
		if self.m_sock is not None:
			try:
				self.m_sock.shutdown(2)
				self.m_sock.close()
			except:
				print "[%s] %s" % (clientproperties._getTime(),clientproperties.CLIENT_ERR_CLOSING_SOCK)
		self.m_die = True

	def _handleInput(self):
		try:
			msg = raw_input()
			
			while(not self._correctResponse(msg)):
				print clientproperties.CLIENT_CHOICE_INVALID
				msg = raw_input()

			self._sendChoiceToServer(msg)
		except KeyboardInterrupt:
			print "[%s] %s" % (clientproperties._getTime(),clientproperties.CLIENT_INTERRUPT_EXITING_MSG)
			self._cleanUp()

	def _correctResponse(self, aMsg):
		if aMsg is None or aMsg.strip() == "":
			return False
		try:
			dummy = int(aMsg)
		except:
			return False

		#for float
		if aMsg != repr(int(aMsg)):
			return False

		num = int(aMsg)
		return (num >= int(clientproperties.CHOICE_MIN) and num <= int(clientproperties.CHOICE_MAX)) and True or False

	def _sendChoiceToServer(self, aMsg):
		if aMsg == clientproperties.CHOICE_SEND_KEY:
			self.m_sock.send(clientproperties.CHOICE_SEND_KEY+"\n")
			(sk,pk, esk) = FHC.getNewKey()
			keysToSend = (pk,esk)
			message = str(keysToSend)
			self.m_sock.send(message+"\n")
			
		elif aMsg == clientproperties.CHOICE_INSERT:
			record = self.readRecord()
			recordToSend = self.encryptRecord(record)
			message = str(recordToSend)
			self.m_sock.send(clientproperties.CHOICE_INSERT+"\n")
			time.sleep(1)
			self.m_sock.send(message+'\n')
		
		elif aMsg == clientproperties.CHOICE_CHECK_ROLL:
			self.m_sock.send(clientproperties.CHOICE_CHECK_ROLL+"\n")
			roll_no = raw_input("Enter roll no:")
			self.m_sock.send(roll_no+"\n")
			msg = self._recv()
			msg = msg.strip()
			print "Id is", msg
		
		elif aMsg == clientproperties.CHOICE_GET_ROW_BY_ID:
			self.m_sock.send(clientproperties.CHOICE_GET_ROW_BY_ID+"\n")
			rowId = raw_input("Enter ID:")
			self.m_sock.send(rowId+"\n")
			msg = self._recv()
			msg = msg.strip()
			record = ast.literal_eval(msg)
			pRecord = self.decryptRecord(record)
			self.displayRecord(pRecord)
			
		elif aMsg == clientproperties.CHOICE_INCREMENT_MARKS_BY_ID:
			pass
		
		elif aMsg == clientproperties.CHOICE_EVAL_TOTAL:
			self.m_sock.send(clientproperties.CHOICE_EVAL_TOTAL+"\n")
			print("Waiting for server response......")
		
		elif aMsg == clientproperties.CHOICE_QUIT:
			self.m_sock.send(clientproperties.CLIENT_SERVER_QUIT_MSG+"\n")
			self._checkQuit(clientproperties.CLIENT_SERVER_QUIT_MSG)
			
	def readRecord(self):
		print "Enter roll number:"
		roll_no = raw_input()
		print "Enter mark 1"
		mark_1 = raw_input()
		print "Enter weight 1"
		weight_1 = raw_input()
		print "Enter mark 2"
		mark_2 = raw_input()
		print "Enter weight 2"
		weight_2 = raw_input()
		return (roll_no,mark_1,weight_1,mark_2,weight_2)
	
	def displayRecord(self, record):
		print "Roll Number: ", record[0]
		print "Mark 1: ", record[1]
		print "Weight 1: ", record[2]
		print "Mark 2: ", record[3]
		print "Weight 2: ", record[4]
		if len(record)>5:
			print "Total: ", record[5]
	
	def encryptRecord(self, record):
		(roll_no,mark_1,weight_1,mark_2,weight_2) = record
		#c_roll_no = FHC.getEncryptedText(roll_mo)
		c_mark_1 = FHC.getEncryptedText(mark_1)
		c_weight_1 = FHC.getEncryptedText(weight_1)
		c_mark_2 = FHC.getEncryptedText(mark_2)
		c_weight_2 = FHC.getEncryptedText(weight_2)
		#return (c_roll_no,c_mark_1,c_weight_1,c_mark_2,c_weight_2)
		return {columns.ROLL: roll_no,columns.MARK_1: c_mark_1,\
			columns.WEIGHT_1: c_weight_1,columns.MARK_2: c_mark_2,\
			 columns.WEIGHT_2: c_weight_2}
	
	def decryptRecord(self, record):
		if record[columns.ROLL] != None:
			roll_no = record[columns.ROLL]
		else:
			roll_no = "0"
			
		if record[columns.MARK_1] != None:
			mark_1 = FHC.getDecryptedText(record[columns.MARK_1])
		else:
			mark_1 = "0"
			
		if record[columns.MARK_2] != None:
			mark_2 = FHC.getDecryptedText(record[columns.MARK_2])
		else:
			mark_2 = "0"
			
		if record[columns.WEIGHT_1] != None:
			weight_1 = FHC.getDecryptedText(record[columns.WEIGHT_1])
		else:
			weight_1 = "0"
			
		if record[columns.WEIGHT_2] != None:
			weight_2 = FHC.getDecryptedText(record[columns.WEIGHT_2])
		else:
			weight_2 = "0"
			
		if record[columns.TOTAL] != None:
			total = FHC.getDecryptedText(record[columns.TOTAL])
		else:
			total = "0"
		return (roll_no,mark_1,weight_1,mark_2,weight_2,total)
	
if __name__ == "__main__":
	FHC.initialize()
	FHC.refreshKeyFromFile()
	client = myclient('nikhil-pc',1234)
	#client = myclient('192.168.1.1',1234)
	client.connect()

