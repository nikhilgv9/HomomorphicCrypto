import socket
import serverproperties
import time
import signal
import sys
import controller
import record
import FHC
import ast
import threading

class killer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.m_servers=[]
		self.start()
		print serverproperties.SERVER_QUIT_KEY_MSG

	def addServer(self,aServer):
		self.m_servers.append(aServer)

	def run(self):
		while True:
			inp = raw_input()				
			if inp in serverproperties.SERVER_QUIT_KEY_LIST:
				print "[%s] %s" % (serverproperties._getTime(),serverproperties.SERVER_QUIT_RECEIVED)
				for i in self.m_servers:
					i._cleanUp()
				sys.exit(2)

_killerObj = killer()

class myserver:
	def __init__(self):
		#server state
		self._initializeServer()
		self.m_dict = {}	#store client info
		self.m_handlers = {}
		self.m_die = False
		_killerObj.addServer(self)

	def _initializeServer(self):
		self.m_addr = (serverproperties.SERVER_NAME, serverproperties.SERVER_PORT)
		self.m_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.m_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.m_sock.bind(self.m_addr)
		self.m_sock.listen(serverproperties.SERVER_MAX_CONN)
	
	def start(self):
		print "[%s] server started" % serverproperties._getTime()
		print "Address: ",(self.m_addr)

		#start listening
		try:
			(clientSock,clientAddr) = self.m_sock.accept()
			self.m_dict[clientSock] = clientAddr
			handler = clienthandler(clientSock,self)
			self.m_handlers[clientSock] = handler
			print "[%s] %s - %s" % (serverproperties._getTime(),serverproperties.SERVER_NEW_CLIENT,clientAddr)
			handler.start()
		except:
			print "[%s] %s" % (serverproperties._getTime(),serverproperties.SERVER_CANNOT_ACCEPT_MSG)
			#raise

	def _cleanUp(self):
		print "[%s] %s %s" % (serverproperties._getTime(),serverproperties.SERVER_CLEANUP_MSG,self.m_addr)
		for k in self.m_dict.keys():
			try:
				k.send(serverproperties.SERVER_CLIENT_QUIT_MSG+'\n')
				k.shutdown(2)
				k.close()
			except:
				print "[%s] %s" % (serverproperties._getTime(),serverproperties.SERVER_ERR_CLOSING_CLIENT_SOCK)
		try:
			self.m_sock.shutdown(2)
			self.m_sock.close()
		except:
			print "[%s] %s" % (serverproperties._getTime(),serverproperties.SERVER_ERR_CLOSING_SOCK)

class clienthandler:
	def __init__(self,aClientSock,aServer):
		self.m_die = False
		self.m_clientSock = aClientSock
		self.m_server = aServer
		self._initializeHandler()

	def _initializeHandler(self):
		self._welcomeClient()

	def _welcomeClient(self):	
		msg = "%s %s" % (serverproperties.SERVER_WELCOME_MSG, repr(self.m_server.m_addr))
		try:
			self.m_clientSock.send(msg+'\n')			
		except:
			print "[%s] %s %s" % (serverproperties._getTime(),serverproperties.SERVER_ERR_CANNOT_SEND,self.m_server.m_dict[self.m_clientSock])
			self.m_clientSock.shutdown(2)
			self.m_clientSock.close()
			self.m_die = True

	def _recv(self, aPrint = True):
		try:		
			buff = self.m_clientSock.recv(serverproperties.SERVER_MAX_RECV)		
			done = False
			while not done:
				if '\n' in buff:
					(line,buff) = buff.split('\n',1)	#split on \n, max 1 split
					if aPrint:
						print "[%s] %s %s:%s" % (serverproperties._getTime(),serverproperties.SERVER_GOT_MSG,self.m_server.m_dict[self.m_clientSock],line)
					else:
						print "[%s] %s %s of length %d" % (serverproperties._getTime(),serverproperties.SERVER_GOT_MSG,self.m_server.m_dict[self.m_clientSock],len(line))

					return line+'\n'
				else:
					more = self.m_clientSock.recv(serverproperties.SERVER_MAX_RECV)
					if not more:
						done = True
					else:
						buff += more

			if buff:
				if aPrint:
						print "[%s] %s %s:%s" % (serverproperties._getTime(),serverproperties.SERVER_GOT_MSG,self.m_server.m_dict[self.m_clientSock],buff)
				else:
					print "[%s] %s of length %s:%d" % (serverproperties._getTime(),serverproperties.SERVER_GOT_MSG,self.m_server.m_dict[self.m_clientSock],len(buff))
				return buff
		except:
			print "[%s] %s" % (serverproperties._getTime(),serverproperties.SERVER_ERR_CANNOT_RECV)
			self.m_die = True

	def start(self):
		while not self.m_die:
			msg = self._recv()
			#msg = self.m_clientSock.recv(1024)
			if msg is not None:
				self._checkAndReply(msg)
		
			#parse it

	def _checkQuit(self,msg):
		if msg.strip() == serverproperties.SERVER_CLIENT_QUIT_MSG:
			self.m_die = True
			self.m_server.m_die = True

	def _checkAndReply(self, aMsg):
		aMsg = aMsg.strip()
		if aMsg == serverproperties.CHOICE_SEND_KEY:
			print "[%s] Receiving key" % serverproperties._getTime()
			msg = self._recv(False).strip()
			print "[%s] Received key" % serverproperties._getTime()
			(pk, esk) = ast.literal_eval(msg)
			FHC.writeKeyToFile("None", pk, esk)
			self.m_clientSock.send(serverproperties.SERVER_OP_SUCCESS+"\n")
		
		elif aMsg == serverproperties.CHOICE_INSERT:
			print "[%s] Receiving Record" % serverproperties._getTime()
			msg = self._recv(False).strip()
			print "[%s] Received Record" % serverproperties._getTime()
			r = ast.literal_eval(msg)
			aRecord = record.recordDTO(r)
			controller.insertRecord(aRecord)
			self.m_clientSock.send(serverproperties.SERVER_OP_SUCCESS+"\n")
		
		elif aMsg == serverproperties.CHOICE_CHECK_ROLL:
			print "[%s] Receiving Query" % serverproperties._getTime()
			msg = self._recv().strip()
			print "[%s] Received Query" % serverproperties._getTime()
			rid=controller.getIdByRollNo(msg)
			self.m_clientSock.send(str(rid)+"\n")
			time.sleep(1)
			self.m_clientSock.send(serverproperties.SERVER_OP_SUCCESS+"\n")
		
		elif aMsg == serverproperties.CHOICE_GET_ROW_BY_ID:
			msg = self._recv()
			if msg is not None:
				dto = controller.getRowById(int(msg.strip()))
			if not self.m_die:			
				try:
					self.m_clientSock.send(repr(dto)+'\n')
				except:
					print "[%s] %s %s" % (serverproperties._getTime(),serverproperties.SERVER_ERR_CANNOT_SEND,self.m_server.m_dict[self.m_clientSock])				
					self.m_die = True
			time.sleep(1)
			self.m_clientSock.send(serverproperties.SERVER_OP_SUCCESS+"\n")
		
		elif aMsg == serverproperties.CHOICE_INCREMENT_MARKS_BY_ID:
			pass
		
		elif aMsg == serverproperties.CHOICE_EVAL_TOTAL:
			rows = controller.getAllRows()
			for row in rows:
				mark1 = row.getMarks1()
				mark2 = row.getMarks2()
				weight1 = row.getWeight1()
				weight2 = row.getWeight2()
				total = FHC.do4BitWeightedSum(mark1, weight1, mark2, weight2)
				row.setTotal(total)
				controller.updateStudentRecord(row)
			self.m_clientSock.send(serverproperties.SERVER_OP_SUCCESS+"\n")
		
		elif aMsg == serverproperties.SERVER_CLIENT_QUIT_MSG:
			self._checkQuit(aMsg)

if __name__ == "__main__":
	FHC.initialize()
	FHC.refreshKeyFromFile()
	serverObj = myserver()
	serverObj.start()