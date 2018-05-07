# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import random
from SEATS_INFO import PlayerInfos
from SEATS_INFO import SeatsInfoList


class Room(KBEngine.Entity):
	"""
	游戏场景
	"""
	def __init__(self):
		DEBUG_MSG("Room cell::__init__")
		KBEngine.Entity.__init__(self)

		self.hasInit = 0
		# 这个房间中所有的玩家
		self.players = {}
		self.playersData = {}
		
		# 这个房间中的所有卡片
		self.cards = [0] * 54
		for i in range(54):
			self.cards[i] = i
		
		#明牌、底牌
		self.openCardIndex = 0
		self.hiddenCards = []
		
		#起始叫牌位、当前叫牌位
		self.startRaiseIndex = 0
		self.raiseIndex = 0

		#最高分、最高分座位
		self.highestPoint = 0
		self.highestPointSeatIndex = 0

		#当前出牌位、最后出牌位
		self.playIndex = 0
		self.lastPlayIndex = 0

		# 让baseapp和cellapp都能够方便的访问到这个房间的entityCall
		KBEngine.globalData["Room_%i" % self.spaceID] = self.base

	def setIsPlaying(self,isPlaying):
		self.isPlaying = isPlaying

	def reqEditRoomInfo(self,roomKey,name,intro):
		DEBUG_MSG("room cell::reqEditRoomInfo:roomKey:%s,name:%s,intro:%s" % (roomKey,name,intro))
		self.name = name
		self.intro = intro

	def reqReadyPlay(self,callerEntityId,roomKey,isReady):
		DEBUG_MSG("Room cell::reqReadyPlay: entityID=%i,roomKey = %s" % (callerEntityId,roomKey))
		for index in range(3):
			if self.playersData.__contains__(index) and self.playersData[index]["id"] == callerEntityId:
				if isReady == 0:
					self.playersData[index]["isReady"] = 1
				else:
					self.playersData[index]["isReady"] = 0
		self.setNewSeatsData()

	def leaveRoom(self, entityCall):
		"""
		defined method.
		某个玩家请求登出服务器并退出这个space
		"""
		DEBUG_MSG("room cell::leaveRoom:entityCallId:%s" % (entityCall.id))
		del self.players[entityCall.id]
		for i in range(3):
			if self.playersData.__contains__(i) and self.playersData[i]["id"] == entityCall.id:#找到退出者的位置i
				if self.playersData[i]["isRoomMamster"] == 1:#如果是房主
					if len(self.playersData) > 1:#如果房间里不止自己
						for j in range(3):
							if self.playersData.__contains__(j) and self.playersData[j]["id"] != entityCall.id and self.playersData[j]["id"] != 0:
								self.playersData[j]["isRoomMamster"] = 1#找到第一个其他玩家，把房主给他。他的准备信息置0
								self.playersData[j]["isReady"] = 0
								break
				self.playersData[i] = {"id":0,"name":"","winCount":0,"loseCount":0,"isReady":0,"seatIndex":i,"isRoomMamster":0}
				break
		self.setNewSeatsData()

	def setNewSeatsData(self):
		DEBUG_MSG("room cell::copyDatas:old playersData:%s" % self.playersData)
		newSeatsData = SeatsInfoList()
		for index in self.playersData:
			playerData = PlayerInfos()
			playerData.extend([self.playersData[index]["id"],self.playersData[index]["name"],self.playersData[index]["winCount"],self.playersData[index]["loseCount"],self.playersData[index]["isReady"],self.playersData[index]["seatIndex"],self.playersData[index]["isRoomMamster"]])
			newSeatsData[index] = playerData
		self.seatsData = newSeatsData

	def setNewInfos(self):
		self.name = self.name
		self.intro = self.intro

		self.hasInit = 0
		self.isGameOver = 0

		for index in range(3):
			self.playersData[index]["isReady"] = 0
		
		#明牌、底牌
		self.openCardIndex = 0
		self.hiddenCards = []
		
		#起始叫牌位、当前叫牌位
		self.startRaiseIndex = 0
		self.raiseIndex = 0

		#最高分、最高分座位
		self.highestPoint = 0
		self.highestPointSeatIndex = 0

		#当前出牌位、最后出牌位
		self.playIndex = 0
		self.lastPlayIndex = 0

	def reqPlayersInfo(self):
		DEBUG_MSG("room cell::reqPlayersInfo")
		self.setNewSeatsData()

	def reqGameInit(self):
		"""
		游戏初始化
		"""
		DEBUG_MSG("Room cell::reqGameInit,cards:%s" % self.cards)
		#洗牌并选出明牌位
		if(self.hasInit < 2):
			if(self.hasInit == 0):
				random.shuffle(self.cards)
				self.openCardIndex = random.randint(0,50)
			self.hasInit += 1
		else:
			#确定起始叫牌位
			self.startRaiseIndex = self.openCardIndex // 17
			self.raiseIndex = self.startRaiseIndex
			#确定明牌与底牌
			self.openCard = self.cards[self.openCardIndex]
			self.hiddenCards = self.cards[51:54]
			DEBUG_MSG("Room cell::reqGameInit,openCard:%s,raiseIndex:%s,hiddenCards:%s" % (self.openCardIndex,self.raiseIndex,self.hiddenCards))
			#发牌
			for index in range(3):
				unSortedhandCards = self.cards[index*17:index*17+17]
				self.players[self.playersData[index]["id"]].handCardsCount = 17
				self.players[self.playersData[index]["id"]].handCards = sorted(unSortedhandCards)
				DEBUG_MSG("Room cell::reqGameInit,name:%s,handCards:%s" % (self.playersData[index]["name"],self.players[self.playersData[index]["id"]].handCards))

	def callPoint(self,callerEntityId,point):
		"""
		叫分
		"""
		DEBUG_MSG("Room cell::callPoint,callerEntityId:%s,point:%s" % (callerEntityId,point))
		#记录最高分与座位号
		if point > self.highestPoint:
			self.highestPoint = point
			self.highestPointSeatIndex = self.players[callerEntityId].seatIndex
		#如果没有叫3分，则下家叫分
		if point != 3:
			#如果三人都叫过分了
			if (self.raiseIndex + 1) % 3 == self.startRaiseIndex:
				#最高分仍然为0则重新开始游戏
				if self.highestPoint == 0:
					self.reqGameInit()
					return
			else:
				self.raiseIndex = (self.raiseIndex + 1) % 3
				return
		#否则最高分者为地主
		self.landlordIndex = self.highestPointSeatIndex
		self.lastPlayIndex = self.landlordIndex
		self.playIndex = self.lastPlayIndex
		for playerId in self.players:
			player = self.players[playerId]
			if player.seatIndex == self.landlordIndex:
				DEBUG_MSG("player.handCards:%s,hiddenCards:%s" % (player.handCards,self.hiddenCards))
				player.handCards.extend(self.hiddenCards)
				DEBUG_MSG("player.handCards:%s" % player.handCards)
				player.handCards = sorted(player.handCards)
				player.handCardsCount += 3
				break
		self.hiddenCardsOpen = self.hiddenCards

	def playCards(self,playCards):
		"""
		出牌
		"""
		self.lastPlayIndex = self.playIndex
		self.lastPlayCards = playCards
		self.passCards()

	def passCards(self):
		"""
		过牌
		"""
		self.playIndex = (self.playIndex+1)%3

	def gameOver(self,callerEntityId):
		"""
		游戏结束
		"""
		self.isGameOver = 1
		self.isPlaying = 1
		self.base.setIsPlaying(1)
		DEBUG_MSG("landlordIndex:%s,callerEntityId:%s,callerSeatIndex:%s" % (self.landlordIndex,callerEntityId,self.players[callerEntityId].seatIndex))
		for playerId in self.players:
			if self.players[playerId].seatIndex == self.landlordIndex:
				if self.players[callerEntityId].seatIndex == self.landlordIndex:
					#地主赢了
					self.players[playerId].winCount += 1
					self.players[playerId].gameResult = 0
				else:
					#地主输了
					self.players[playerId].loseCount += 1
					self.players[playerId].gameResult = 1
			else:
				if self.players[callerEntityId].seatIndex == self.landlordIndex:
					#农民赢了
					self.players[playerId].loseCount += 1
					self.players[playerId].gameResult = 1
				else:
					#农民输了
					self.players[playerId].winCount += 1
					self.players[playerId].gameResult = 0
			self.players[playerId].writeToDB()
			
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, id, userArg):
		"""
		KBEngine method.
		使用addTimer后， 当时间到达则该接口被调用
		@param id		: addTimer 的返回值ID
		@param userArg	: addTimer 最后一个参数所给入的数据
		"""

	def onDestroy(self):
		"""
		KBEngine method.
		"""
		DEBUG_MSG("Room cell::onDestroy: %i" % (self.id))
		del KBEngine.globalData["Room_%i" % self.spaceID]
		
	def onDestroyTimer(self):
		DEBUG_MSG("Room cell::onDestroyTimer: %i" % (self.id))
		# 请求销毁引擎中创建的真实空间，在空间销毁后，所有该空间上的实体都被销毁
		self.destroySpace()
		
	def onEnter(self, entityCall):
		"""
		defined method.
		进入场景
		"""
		DEBUG_MSG('Room cell::onEnter space[%d] entityID = %i.' % (self.spaceID, entityCall.id))
		self.players[entityCall.id] = entityCall
		for index in range(3):
			if not self.playersData.__contains__(index) or self.playersData[index]["id"] == 0:
				entityCall.seatIndex = index
				self.playersData[index] = {"id":entityCall.id,"name":entityCall.nameC,"winCount":entityCall.winCount,"loseCount":entityCall.loseCount,"isReady":0,"seatIndex":index,"isRoomMamster":0}
				if len(self.playersData) == 1:
					self.playersData[index]["isRoomMamster"] = 1
				break
		self.setNewSeatsData()

	def onLeave(self, entityID):
		"""
		defined method.
		离开场景
		"""
		DEBUG_MSG('Room cell::onLeave space[%d] entityID = %i.' % (self.spaceID, entityID))