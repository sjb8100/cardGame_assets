# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon

TIMER_TYPE_ADD_TRAP = 1

class Account(KBEngine.Entity, EntityCommon):
	def __init__(self):
		KBEngine.Entity.__init__(self)
		EntityCommon.__init__(self)

		#self.handCards = []
		#self.handCardsCount = 0
		#self.playCards = []
		
		self.getCurrRoom().onEnter(self)

	def reqRoomInfo(self,callerEntityId,roomKey):
		self.getCurrRoom().setNewInfos()
		self.getCurrRoom().setNewSeatsData()

	def reqEditRoomInfo(self,callerEntityId,roomKey,name,intro):
		"""
		请求修改房间信息
		"""
		DEBUG_MSG("Account cell::reqEditRoomInfo:callerEntityId:%s,roomKey:%s,name:%s,intro:%s" % (callerEntityId,roomKey,name,intro))
		self.getCurrRoom().reqEditRoomInfo(roomKey,name,intro)

	def reqReadyPlay(self,callerEntityId,roomKey,isReady):
		"""
		请求准备
		"""
		DEBUG_MSG("Account cell::reqReadyPlay:callerEntityId:%s,roomKey:%i,isReady:%s" % (callerEntityId,roomKey,isReady))
		self.getCurrRoom().reqReadyPlay(callerEntityId,roomKey,isReady)

	def reqPlayersInfo(self,callerEntityId,roomKey):
		"""
		请求玩家信息
		"""
		DEBUG_MSG("Account cell::reqPlayersInfo:roomKey:%s" % roomKey)
		self.getCurrRoom().reqPlayersInfo()

	def reqGameInit(self,callerEntityId,roomKey):
		"""
		请求游戏初始化
		"""
		DEBUG_MSG("Account cell::reqGameInit:callerEntityId:%s,roomKey:%s" % (callerEntityId,roomKey))
		self.getCurrRoom().reqGameInit()

	def callPoint(self,callerEntityId,point):
		"""
		请求叫牌
		"""
		DEBUG_MSG("Account cell::callPoint:callerEntityId:%s,point:%s" % (callerEntityId,point))
		self.getCurrRoom().callPoint(callerEntityId,point)
		self.message = point

	def reqPlayCards(self,callerEntityId,cardsList):
		"""
		请求出牌
		"""
		self.playCards = []
		DEBUG_MSG("Account cell::reqPlayCards:callerEntityId:%s,cardsList:%s" % (callerEntityId,cardsList))
		DEBUG_MSG("Account cell::reqPlayCards:handCards:%s,playCards:%s" % (self.handCards,self.playCards))
		self.checkCardsType(cardsList)
		for cardIndex in cardsList:
			self.handCards.remove(cardIndex)
			self.playCards.append(cardIndex)
		newHandCards = []
		newHandCards.extend(self.handCards)
		self.handCards = newHandCards
		newPlayCards = []
		newPlayCards.extend(self.playCards)
		self.playCards = newPlayCards
		self.handCardsCount -= len(cardsList)
		DEBUG_MSG("Account cell::reqPlayCards:handCards:%s,playCards:%s" % (self.handCards,self.playCards))
		if self.handCardsCount == 0:
			self.getCurrRoom().gameOver(callerEntityId)
		else:
			self.getCurrRoom().playCards(self.playCards)

	def checkCardsType(self,cardsList):
		"""
		检查牌型
		"""
		DEBUG_MSG("Account cell::checkCardsType:cardsList:%s" % cardsList)
		pass

	def passCards(self,callerEntityId,passCode):
		"""
		请求过牌
		"""
		DEBUG_MSG("Account cell::pass:callerEntityId:%s" % callerEntityId)
		self.getCurrRoom().passCards()
		self.message = passCode

	def reqAddCard(self,callerEntityId,color,cardNum):
		"""
		请求加一张牌
		"""
		DEBUG_MSG("Account cell::reqAddCard:callerEntityId:%s,cardNum:%s" % (callerEntityId,cardNum))
		if cardNum == 52 or cardNum == 53:
			cardIndex = cardNum
		else:
			cardIndex = (cardNum + 10) % 13 * 4 + color
		if self.handCards.__contains__(cardIndex):
			return
		self.handCardsCount += 1
		newHandCards = []
		newHandCards.extend(self.handCards)
		newHandCards.append(cardIndex)
		newHandCards = sorted(newHandCards)
		self.handCards = newHandCards

	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.className, self.id, tid, userArg))
		EntityCommon.onTimer(self, tid, userArg)

	def onUpgrade(self):
		pass
	

	def onGetWitness(self):
		"""
		KBEngine method.
		绑定了一个观察者(客户端)
		"""
		DEBUG_MSG("Account cell::onGetWitness: %i." % self.id)

	def onLoseWitness(self):
		"""
		KBEngine method.
		解绑定了一个观察者(客户端)
		"""
		DEBUG_MSG("Account cell::onLoseWitness: %i." % self.id)
	
	def onDestroy(self):
		"""
		KBEngine method.
		entity销毁
		"""
		DEBUG_MSG("Account cell::onDestroy: %i." % self.id)
		self.getCurrRoom().leaveRoom(self)