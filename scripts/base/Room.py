# -*- coding: utf-8 -*-
import KBEngine
import random
import copy
import math
from KBEDebug import *

class Room(KBEngine.Entity):
	"""
	一个可操控cellapp上真正space的实体
	注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		
		# 请求在cellapp上创建cell空间
		self.createCellEntityInNewSpace(None)
		
		self.accounts = {}

	def enterRoom(self, entityCall):
		"""
		defined method.
		请求进入某个space中
		"""
		DEBUG_MSG("room base::enterRoom:current accounts:%s" % self.accounts)
		entityCall.createCell(self)
		self.onEnter(entityCall)

	def leaveRoom(self, entityID):
		"""
		defined method.
		某个玩家请求退出这个space
		"""
		DEBUG_MSG("room base::leaveRoom:entityId:%s" % entityID)
		self.onLeave(entityID)

	def setIsPlaying(self,isPlaying):
		roomData = KBEngine.globalData["Hall"].findRoom(self.roomKey)
		roomData["isPlaying"] = isPlaying
		
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		pass
		
	def onEnter(self, entityCall):
		"""
		defined method.
		进入场景
		"""
		DEBUG_MSG("room base::onEnter:entitycall:%s,roomKey:%s" % (entityCall,self.roomKey))
		self.accounts[entityCall.id] = entityCall
		
	def onLeave(self, entityID):
		"""
		defined method.
		离开场景
		"""
		DEBUG_MSG("room base::onLeave:entityId:%s" % entityID)
		if entityID in self.accounts:
			del self.accounts[entityID]

	def onLoseCell(self):
		"""
		KBEngine method.
		entity的cell部分实体丢失
		"""
		DEBUG_MSG("room base::onLoseCell:roomKey:%s" % roomKey)
		KBEngine.globalData["Hall"].onRoomLoseCell(self.roomKey)
		
		self.accounts = {}
		self.destroy()

	def onGetCell(self):
		"""
		KBEngine method.
		entity的cell部分实体被创建成功
		"""
		DEBUG_MSG("Room base::onGetCell: %i" % self.id)
		KBEngine.globalData["Hall"].onRoomGetCell(self, self.roomKey)

	def destroySelf(self):
		"""
		"""
		DEBUG_MSG("Room base::destroy room")
		
		# 必须先销毁cell实体，才能销毁base
		DEBUG_MSG("Room base::destroy cell")
		if self.cell is not None:
			self.destroyCellEntity()
			return

		# 销毁base
		DEBUG_MSG("Room base::destroy base")
		self.destroy()
