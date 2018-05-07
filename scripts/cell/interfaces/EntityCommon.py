# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import * 

class EntityCommon:
	"""
	服务端游戏对象的基础接口类
	"""
	def __init__(self):
		pass

	def initEntity(self):
		"""
		virtual method.
		"""
		pass
	
	def isAvatar(self):
		"""
		virtual method.
		"""
		return False
	
	def getCurrRoomBase(self):
		"""
		获得当前space的entity baseEntityCall
		"""
		return KBEngine.globalData.get("Room_%i" % self.spaceID)

	def getCurrRoom(self):
		"""
		获得当前space的entity
		"""
		roomBase = self.getCurrRoomBase()
		if roomBase is None:
			return roomBase

		return KBEngine.entities.get(roomBase.id, None)
		
	def getHall(self):
		"""
		获取场景管理器
		"""
		return KBEngine.globalData["Hall"]
	
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
			
	def onRestore(self):
		"""
		KBEngine method.
		entity的cell部分实体被恢复成功
		"""
		DEBUG_MSG("%s::onRestore: %s" % (self.className, self.base))
