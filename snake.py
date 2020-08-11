import sched, time
import os

import sys
import select
import tty
import termios

from queue import Queue
from threading import Thread
from random import randrange

class Vector:
	'Vector'
	def __init__(self, x,y):
		self.x = x
		self.y = y

class Board:
	'class for board'
	def __init__(self, x, y):
		self.width = x
		self.height = y
		self.boardValue = [[' ' for i in range(x + 2)] for j in range(y + 2)]
		#draw board
		for j in range(len(self.boardValue[0])):
			self.boardValue[0][j] = '-'
		
		for j in range(len(self.boardValue[len(self.boardValue) - 1])):
			self.boardValue[len(self.boardValue) - 1][j] = '-'

		for i in range(len(self.boardValue)):
			self.boardValue[i][0] = '|'

		for i in range(len(self.boardValue)):
			self.boardValue[i][len(self.boardValue[i]) - 1] = '|'
	def SetValue(self, x, y, val):
		self.boardValue[x + 1][ y + 1] = val

class Snake:
	'class for snake'
	increase = False
	speed = Vector(-1, 0)
	def __init__(self, bodyList):
		self.bodyList = bodyList
	def UpdatePosition(self):
		print(self.speed.x)
		print(self.speed.y)

		newHead = Vector(self.bodyList[0].x + self.speed.x, self.bodyList[0].y + self.speed.y)
		self.bodyList.insert(0, newHead)
		if(self.increase == False):
			self.bodyList.pop(len(self.bodyList) - 1)
		else:
			self.increase = False

		for i in range(1, len(self.bodyList)):
			if(newHead.x == self.bodyList[i].x and newHead.y == self.bodyList[i].y):
				return False
		return True

	def CheckIncrease(self, meatPosition):
		newHead = Vector(self.bodyList[0].x + self.speed.x, self.bodyList[0].y + self.speed.y)
		if(newHead.x == meatPosition.x and newHead.y == meatPosition.y):
			self.increase = True
			return True
		return False

class Main:
	'Main'

	score = 0
	currentInput = 'a'
	meat = Vector(10, 10)
	alive = True
	count = 0
	refreshSpeed = 1
	scheduler = sched.scheduler(time.time, time.sleep)

	def __init__(self, refreshSpeed = 1):
		#init refresh speed
		self.refreshSpeed = refreshSpeed
		#init baord
		self.board = Board(21, 21)
		#init snake
		firstBody = Vector(int(self.board.width/2) - 1, int(self.board.height/2))
		secondBody = Vector(int(self.board.width/2), int(self.board.height/2))
		thirdBody = Vector(int(self.board.width/2) + 1, int(self.board.height/2))
		forthBody = Vector(int(self.board.width/2) + 2, int(self.board.height/2))
		fifthBody = Vector(int(self.board.width/2) + 3, int(self.board.height/2))
		self.snake = Snake([firstBody, secondBody, thirdBody, forthBody, fifthBody])

	def Start(self):
		self.scheduler.run()

	def Refresh(self, sc, q):
		self.GetSpeed()
		needNewMeat = self.snake.CheckIncrease(self.meat);
		self.alive = self.snake.UpdatePosition()
		self.alive = self.alive and self.Judge()
		if(needNewMeat):
			self.NewMeat()
			self.score += 1
		self.Render()
		if(self.alive == False):
			return
		self.count += self.refreshSpeed
		self.schedulerEvent = self.scheduler.enter(self.refreshSpeed, 1, self.Refresh, (sc, q))

	def NewMeat(self):
		self.meat.x = randrange(0, self.board.width)
		self.meat.y = randrange(0, self.board.height)
		while(not self.CheckMeatLegit()):
			self.meat.x = randrange(0, self.board.width)
			self.meat.y = randrange(0, self.board.height)

	def CheckMeatLegit(self):
		for body in self.snake.bodyList:
			if(self.meat.x == body.x and self.meat.y == body.y):
				return False
		return True

	def Judge(self):
		if(self.snake.bodyList[0].x >= self.board.width or self.snake.bodyList[0].x < 0 
			or self.snake.bodyList[0].y >= self.board.height or self.snake.bodyList[0].y < 0 ):
			return False

	def Render(self):
		#clean board
		_ = os.system('clear')
		#draw counter
		print('score:' + str(self.score))
		print('Time:' + str( int(self.count)))
		print("\n")
		#update board
		for i in range(self.board.height):
			for j in range(self.board.width):
				self.board.SetValue(i, j, ' ')

		for body in self.snake.bodyList:
			self.board.SetValue(body.y, body.x, 1)
		self.board.SetValue(self.snake.bodyList[0].y, self.snake.bodyList[0].x, 0)

		if(self.meat.x >= 0 and self.meat.y >= 0):
			self.board.SetValue(self.meat.y, self.meat.x, '6')

		if(self.alive == False):
			self.board.SetValue(int(self.board.height/2), int(self.board.width/2), '菜')
			self.board.SetValue(int(self.board.height/2), int(self.board.width) - 2, '')

		#draw board
		for i in range(len(self.board.boardValue)):
			for j in range(len(self.board.boardValue[i])):
				print(self.board.boardValue[i][j], end = '')
			print("")

	def GetSpeed(self):
		if(self.currentInput == 'w'):
			if(self.snake.speed.y != 1):
				self.snake.speed.x = 0
				self.snake.speed.y = -1
		elif(self.currentInput == 's'):
			if(self.snake.speed.y != -1):
				self.snake.speed.x = 0
				self.snake.speed.y = 1
		elif(self.currentInput == 'a'):
			if(self.snake.speed.x != 1):
				self.snake.speed.x = -1
				self.snake.speed.y = 0
		elif(self.currentInput == 'd'):
			if(self.snake.speed.x != -1):
				self.snake.speed.x = 1
				self.snake.speed.y = 0

	def InputReceived(self, input):
		self.currentInput = input;
		

def GameLoop(main, int_q):
	main.schedulerEvent = main.scheduler.enter(main.refreshSpeed, 1, main.Refresh, (main.scheduler, int_q))
	main.Start()

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def InputLoop(main, out_q):
	old_settings = termios.tcgetattr(sys.stdin)
	try:
		tty.setcbreak(sys.stdin.fileno())

		while 1:
			if isData():
				c = sys.stdin.read(1)
				main.InputReceived(c)

	finally:
	    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

q = Queue()
main = Main(0.1)
t2 = Thread(target = GameLoop, args = (main, q))
t2.start()
t1 = Thread(target = InputLoop, args = (main, q))
t1.start()