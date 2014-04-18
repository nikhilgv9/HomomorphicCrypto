#! /usr/bin/python
import time

def _getTime():
	return time.strftime("%d-%b-%Y %H:%M:%S",time.localtime(time.time()))

CLIENT_CANNOT_CONNECT_MSG = "Could not connect to server"
CLIENT_CONNECTED_MSG = "Connected to server"
CLIENT_ERR_CANNOT_RECV = "Could not receive from server"
CLIENT_ERR_CANNOT_SEND = "Could not send to server"
CLIENT_INTERRUPT_EXITING_MSG = "Keyboard interrupt client exiting"
CLIENT_CLEANUP_MSG = "Cleaning up"
CLIENT_SERVER_QUIT_MSG = "##QUIT##"
CLIENT_QUIT_REQUEST_MSG = "Client quit request received"
CLIENT_MAX_SEND = CLIENT_MAX_RECV = 4096
CLIENT_ERR_CLOSING_SOCK = "Error closing socket"
CLIENT_CHOICE_INVALID = "Invalid input, re-enter:"
CLIENT_MENU = ("Actions for server: ","1. Send key", "2. Insert record", "3. Check if Roll No is present", "4. Get row by ID", "5. Increment marks of ID", "6. Evaluate values of total column", "7. Exit", "Enter a choice:")
CHOICE_MIN = "1"
CHOICE_MAX = "7"
CHOICE_SEND_KEY = "1"
CHOICE_INSERT = "2"
CHOICE_CHECK_ROLL = "3"
CHOICE_GET_ROW_BY_ID = "4"
CHOICE_INCREMENT_MARKS_BY_ID = "5"
CHOICE_EVAL_TOTAL = "6"
CHOICE_QUIT = "7"
SERVER = "Server"
