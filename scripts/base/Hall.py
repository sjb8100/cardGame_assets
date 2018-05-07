# -*- coding: utf-8 -*-
import KBEngine
import Functor
from KBEDebug import *
import traceback
from ROOM_INFOS import RoomInfosList
from ROOM_INFOS import RoomInfos

FIND_ROOM_NOT_FOUND = 0
FIND_ROOM_CREATING = 1

class Hall(KBEngine.Entity):
	"""
	这是一个脚本层封装的房间管理器
	"""
	def __init__(self):
		KBEngine.Entity.__init__(self)
		
		# 向全局共享数据中注册这个管理器的entityCall以便在所有逻辑进程中可以方便的访问
		KBEngine.globalData["Hall"] = self

		# 所有房间，是个字典结构
		# enterRoomReqs, 在房间未创建完成前， 请求进入房间和登陆到房间的请求记录在此，等房间建立完毕将他们扔到space中
		self.rooms = {}
		self.roomSearchResult = RoomInfosList()

	def findRoom(self, roomKey):
		"""
		根据key查找一个指定房间
		"""
		DEBUG_MSG("Hall::findRoom:roomKey%s" % roomKey)
		roomDatas = self.rooms.get(roomKey)
		# 如果房间没有创建，则返回错误
		if not roomDatas:
			return 0
		return roomDatas

	def reqRoomsByParams(self, nameOrIntro, isFull, isPlaying, hasPassword):
		"""
		查找所有符合条件的房间
		"""
		self.roomSearchResult = RoomInfosList()
		DEBUG_MSG("Hall::reqRoomsByRarams:nameOrIntro:%s,isFull:%s,isPlaying:%s,hasPassword:%s" % (nameOrIntro,isFull,isPlaying,hasPassword))
		for roomKey in self.rooms:
			room = self.rooms.get(roomKey)
			if nameOrIntro == "" or (nameOrIntro in room["name"] or nameOrIntro in room["intro"]):
				if isFull == 0 or (isFull == 1 and room["playerCount"] < 3) or (isFull == 2 and room["playerCount"] == 3):
					if isPlaying == 0 or isPlaying == room["isPlaying"]:
						if hasPassword == 0 or hasPassword == room["hasPassword"]:
							roomData = RoomInfos()
							roomData.extend([room["roomKey"], room["name"], room["intro"], room["playerCount"], room["isPlaying"], room["hasPassword"]])
							self.roomSearchResult[roomData[0]] = roomData

		return self.roomSearchResult

	def reqCreateRoom(self, entityCall, name, intro, password):
		"""
		请求创建房间
		"""
		DEBUG_MSG("Hall::reqCreateRoom:name:%s,intro:%s，password:%s" % (name, intro, password))
		self.newRoomKey = KBEngine.genUUID64()

		KBEngine.createEntityAnywhere("Room", \
									{
									"roomKey"     : self.newRoomKey,
									"name"        : name,
									"intro"       : intro,
									"password"    : password
									}, \
									Functor.Functor(self.onRoomCreatedCB, self.newRoomKey))
		if password == "":
			hasPassword = 1;
		else:
			hasPassword = 2;

		roomDatas = {"roomEntityCall" : None, "playerCount": 0, "roomKey" : self.newRoomKey, "name" : name, "intro":intro,"password":password,"isPlaying":1, "hasPassword":hasPassword, "enterRoomReqs" : []}
		self.rooms[self.newRoomKey] = roomDatas
		DEBUG_MSG("Hall::reqCreateRoom:rooms:%s" % self.rooms)

		entityCall.reqJoinRoom(self.newRoomKey,password)

	def reqJoinRoom(self, entityCall, roomKey,password):
		"""
		请求进入某个Room中
		"""
		DEBUG_MSG("Hall::reqJoinRoom: space %i creating..., enter entityID=%i" % (roomKey, entityCall.id))
		roomDatas = self.findRoom(roomKey)
		if roomDatas == 0:
			DEBUG_MSG("Hall:reqJoinRoom: room is not exist")
			return 27
		if roomDatas["playerCount"] == 3:
			DEBUG_MSG("Hall:reqJoinRoom: room is full")
			return 28
		if roomDatas["hasPassword"] == 2 and roomDatas["password"] != password:
			DEBUG_MSG("Hall:enterRoom: password is not valid")
			return 29
		entityCall.roomKey = roomKey
		roomDatas["playerCount"] += 1
		
		return 0

	def reqEnterWorld(self,entityCall,roomKey):
		DEBUG_MSG("Hall:reqEnterWorld,roomKey:%s" % roomKey)
		roomDatas = self.findRoom(roomKey)
		DEBUG_MSG("Hall:reqEnterWorld:roomDatas:%s" % roomDatas)
		roomEntityCall = roomDatas["roomEntityCall"]
		if roomEntityCall is not None:
			roomEntityCall.enterRoom(entityCall)
		else:
			roomDatas["enterRoomReqs"].append(entityCall)

	def leaveRoom(self,entityCall,roomKey):
		DEBUG_MSG("Hall::leaveRoom:entityCall:%s,roomKey:%s" % (entityCall,roomKey))
		roomDatas = self.findRoom(roomKey)
		roomEntityCall = roomDatas["roomEntityCall"]
		roomEntityCall.leaveRoom(entityCall.id)
		roomDatas["playerCount"] -= 1
		if roomDatas["playerCount"] == 0:
			roomEntityCall.destroySelf()
			del self.rooms[roomKey]
		
	#--------------------------------------------------------------------------------------------
	#                              Callbacks
	#--------------------------------------------------------------------------------------------
	def onRoomCreatedCB(self, roomKey, roomEntityCall):
		"""
		一个space创建好后的回调
		"""
		DEBUG_MSG("Hall::onRoomCreatedCB: space %i. entityID=%i" % (roomKey, roomEntityCall.id))

	def onTimer(self, tid, userArg):
		"""
		KBEngine method.
		引擎回调timer触发
		"""
		#DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
		pass
		
	def onRoomLoseCell(self, roomKey):
		"""
		defined method.
		Room的cell销毁了
		"""
		DEBUG_MSG("Hall::onRoomLoseCell: space %i." % (roomKey))
		del self.rooms[roomKey]

	def onRoomGetCell(self, roomEntityCall, roomKey):
		"""
		defined method.
		Room的cell创建好了
		"""
		DEBUG_MSG("Hall::onRoomGetCell: space %i." % (roomKey))
		self.rooms[roomKey]["roomEntityCall"] = roomEntityCall

		# space已经创建好了， 现在可以将之前请求进入的玩家全部丢到cell地图中
		for entityCall in self.rooms[roomKey]["enterRoomReqs"]:
			DEBUG_MSG("Hall::onRoomGetCell:entity:%s,room:%s" % (entityCall,roomEntityCall))
			#entityCall.createCell(roomEntityCall)
			roomEntityCall.enterRoom(entityCall)
			
		self.rooms[roomKey]["enterRoomReqs"] = []