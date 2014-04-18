#! /usr/bin/python
import socket
import time

SERVER_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(SERVER_NAME)	#localhost always
LOCALHOST_ADDR = "127.0.0.1"
LOCALHOST_NAME = "localhost"
SERVER_PORT = 1234
DB_NAME = 'cryptodb'
DB_USERNAME = 'root'
DB_PASSWORD = 'nnn'	#fill in
SERVER_MAX_CONN = 1
SERVER_THREAD_ID_MULTIPLIER = 10000000	#this is multiplied by current time floating number
SERVER_THREAD_NAME_PREFIX = "CRYPT_SERVER"
HANDLER_THREAD_NAME_PREFIX = "CRYPT_HANDLER"
SERVER_NEW_CLIENT = "Client connected"
SERVER_WELCOME_MSG = "Successfully connected to"
SERVER_ERR_CANNOT_SEND = "Could not send to client"
SERVER_ERR_CANNOT_RECV = "Could not get data from client"
SERVER_GOT_MSG = "Received from"
SERVER_TEST_MSG = "Test message"
SERVER_CLIENT_QUIT_MSG = "##QUIT##"
SERVER_CLIENT_WANTS_TO_QUIT = "Quit message received from"
SERVER_QUIT_KEY_MSG = "Press q to quit"
SERVER_QUIT_RECEIVED = "Server quit request received"
SERVER_QUIT_MSG = "Quitting server"
SERVER_QUIT_KEY_LIST = ['q','Q']
SERVER_CLEANUP_MSG = "Cleaning up"
SERVER_CANNOT_ACCEPT_MSG = "Cannot accept"
SERVER_MAX_RECV = SERVER_MAX_SEND = 4096
SERVER_ERR_CLOSING_CLIENT_SOCK = "Error closing client socket"
SERVER_ERR_CLOSING_SOCK = "Error closing server socket"
SERVER_OP_SUCCESS = "Operation succeeded"
CHOICE_MIN = "1"
CHOICE_MAX = "7"
CHOICE_SEND_KEY = "1"
CHOICE_INSERT = "2"
CHOICE_CHECK_ROLL = "3"
CHOICE_GET_ROW_BY_ID = "4"
CHOICE_INCREMENT_MARKS_BY_ID = "5"
CHOICE_EVAL_TOTAL = "6"
CHOICE_QUIT = "7"

def _getTime():
	return time.strftime("%d-%b-%Y %H:%M:%S",time.localtime(time.time()))