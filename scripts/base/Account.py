# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class Account(KBEngine.Proxy):
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		self.cellData["dbid"] = self.id
		self.cellData["nameC"] = self.name
		
	def createCell(self, space):
		"""
		defined method.
		创建cell实体
		"""
		DEBUG_MSG("account base::createCell:account id:%s,space id:%s" % (self.id,space.roomKey))
		if self.cell == None:
			self.createCellEntity(space.cell)
			self.roomKey = space.roomKey

	def destroySelf(self):
		"""
		"""
		DEBUG_MSG("Account base::destroySelf")
		KBEngine.globalData["Hall"].leaveRoom(self,self.roomKey)
		
		# 必须先销毁cell实体，才能销毁base
		if self.cell is not None:
			DEBUG_MSG("Account base::destroy cell")
			self.destroyCellEntity()
			DEBUG_MSG("Account base::cell:%s" % self.cell)
			return

		# 销毁base
		DEBUG_MSG("Account base::destroy base")
		self.roomKey = 0
		self.writeToDB()
		self.destroy()

	def reqSetName(self, name):
		"""
		请求设定昵称
		"""

		if(self.name != ''):
			DEBUG_MSG("Account cell::name is exist,name:%s" % self.name)
			retcode = 25
			self.client.onSetNameFailed(retcode, name)
			return
		if(name == ''):
			DEBUG_MSG("Account cell::name is null")
			retcode = 26
			self.client.onSetNameFailed(retcode, name)
			return

		self.name = name
		DEBUG_MSG("Account cell::set name: %s." % name)
		
		self.writeToDB()

		if self.client:
			self.client.onSetNameSuccessfully(name)
		

	def reqCreateRoom(self, name, intro, password):
		"""
		请求创建房间
		"""
		DEBUG_MSG("Account base::reqCreateRoom:name:%s,intro:%s,password:%s" % (name,intro,password))
		KBEngine.globalData["Hall"].reqCreateRoom(self,name,intro,password)

	def reqRoomsByParams(self,nameOrIntro,isFull,isPlaying,hasPassword):
		"""
		请求所有符合条件的房间
		"""
		DEBUG_MSG("Account base::reqRoomsByParams:nameOrIntro:%s,isFull:%i,isPlaying:%i,hasPassword:%i" % (nameOrIntro,isFull,isPlaying,hasPassword))
		roomsResult = KBEngine.globalData["Hall"].reqRoomsByParams(nameOrIntro,isFull,isPlaying,hasPassword)

		DEBUG_MSG("Account base::rooms result:%s" % roomsResult)
		self.client.onReqRoomsByParams(roomsResult)

	def reqJoinRoom(self,roomKey,password):
		"""
		请求进入房间
		"""
		DEBUG_MSG("Account base::reqJoinRoom:roomKey:%i" % roomKey)
		retcode = KBEngine.globalData["Hall"].reqJoinRoom(self,roomKey,password)
		if(retcode != 0):
			self.client.onReqJoinRoomFailed(retcode)
		else:
			self.client.onReqJoinRoomSuccess(retcode)

	def reqEnterWorld(self,roomKey):
		"""
		进入房间
		"""
		DEBUG_MSG("Account base::enterWorld:roomKey:%i" % roomKey)
		KBEngine.globalData["Hall"].reqEnterWorld(self,roomKey)

	def reqRoomPassword(self,roomKey):
		"""
		请求房间密码
		"""
		DEBUG_MSG("Account base::reqEditRoomPassword:roomKey:%i" % roomKey)
		roomDatas = KBEngine.globalData["Hall"].findRoom(roomKey)
		self.client.onReqRoomPassword(roomDatas["password"])

	def reqEditRoomPassword(self,roomKey,password):
		"""
		请求修改房间密码
		"""
		DEBUG_MSG("Account base::reqEditRoomPassword:roomKey:%i,password:%s" % (roomKey,password))
		roomDatas = KBEngine.globalData["Hall"].findRoom(roomKey)
		roomDatas["password"] = password
		if password == "":
			roomDatas["hasPassword"] = 1
		else:
			roomDatas["hasPassword"] = 2

	def reqExitRoom(self,roomKey):
		"""
		请求退出房间
		"""
		DEBUG_MSG("Account base::reqExitRoom:roomKey:%i" % roomKey)
		KBEngine.globalData["Hall"].leaveRoom(self,roomKey)
		self.destroyCellEntity()
		self.client.onReqExitRoom(self.id)

	def reqPlayGame(self,roomKey):
		"""
		请求开始游戏
		"""
		DEBUG_MSG("Account base::reqPlayGame:roomKey:%s" % roomKey)
		roomDatas = KBEngine.globalData["Hall"].findRoom(roomKey)
		roomDatas["isPlaying"] = 2
		roomCell = roomDatas["roomEntityCall"].cell.setIsPlaying(2)

	def reqExitGame(self,roomKey):
		"""
		请求退出游戏
		"""
		DEBUG_MSG("Account base::reqExitGame:roomKey:%i" % roomKey)
		KBEngine.globalData["Hall"].leaveRoom(self,roomKey)
		self.destroyCellEntity()

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
		DEBUG_MSG(id, userArg)
		
	def onClientEnabled(self):
		"""
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。
		"""
		INFO_MSG("Account base::onClientEnabled:account[%i] entities enable. entityCall:%s" % (self.id, self.client))
		if self.name == "":
			self.client.onEnterSetName(self.name)
		else:
			self.client.onEnterHall(self.id)
			
			
	def onLogOnAttempt(self, ip, port, password):
		"""
		KBEngine method.
		客户端登陆失败时会回调到这里
		"""
		INFO_MSG(ip, port, password)
		return KBEngine.LOG_ON_ACCEPT

	def onGetCell(self):
		"""
		KBEngine method.
		entity的cell部分实体被创建成功
		"""
		DEBUG_MSG('Account base::onGetCell: %s' % self.cell)

	def onLoseCell(self):
		"""
		KBEngine method.
		entity的cell部分实体丢失
		"""
		DEBUG_MSG("Account base::onLoseCell: %i" % (self.id))
		
	def onClientDeath(self):
		"""
		KBEngine method.
		客户端对应实体已经销毁
		"""
		DEBUG_MSG("Account base::onClientDeath:Account[%i]" % self.id)
		self.destroySelf()