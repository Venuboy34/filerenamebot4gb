import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client['RenameBot']
        self.users = self.db['users']
        self.chats = self.db['chats']

    # User Management
    async def add_user(self, user_id, user_name):
        user = await self.users.find_one({'id': user_id})
        if not user:
            await self.users.insert_one({
                'id': user_id,
                'name': user_name,
                'expiry_time': None,
                'thumbnail': None,
                'upload_as_doc': True  # Default: upload as document
            })

    async def get_user(self, user_id):
        return await self.users.find_one({'id': user_id})

    async def update_user(self, user_data):
        await self.users.update_one(
            {'id': user_data['id']},
            {'$set': user_data},
            upsert=True
        )

    async def remove_premium_access(self, user_id):
        user = await self.get_user(user_id)
        if user and user.get('expiry_time'):
            await self.users.update_one(
                {'id': user_id},
                {'$set': {'expiry_time': None}}
            )
            return True
        return False

    async def get_all_users(self):
        return self.users.find({})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def delete_user(self, user_id):
        await self.users.delete_one({'id': user_id})

    # Thumbnail Management
    async def set_thumbnail(self, user_id, file_id):
        await self.users.update_one(
            {'id': user_id},
            {'$set': {'thumbnail': file_id}},
            upsert=True
        )

    async def get_thumbnail(self, user_id):
        user = await self.get_user(user_id)
        return user.get('thumbnail') if user else None

    async def delete_thumbnail(self, user_id):
        await self.users.update_one(
            {'id': user_id},
            {'$set': {'thumbnail': None}}
        )

    # Upload Settings
    async def set_upload_mode(self, user_id, upload_as_doc):
        await self.users.update_one(
            {'id': user_id},
            {'$set': {'upload_as_doc': upload_as_doc}},
            upsert=True
        )

    async def get_upload_mode(self, user_id):
        user = await self.get_user(user_id)
        return user.get('upload_as_doc', True) if user else True

    # Chat Management
    async def add_chat(self, chat_id, chat_name):
        chat = await self.chats.find_one({'id': chat_id})
        if not chat:
            await self.chats.insert_one({
                'id': chat_id,
                'name': chat_name
            })

    async def get_all_chats(self):
        return self.chats.find({})

    async def total_chat_count(self):
        return await self.chats.count_documents({})

    async def delete_chat(self, chat_id):
        await self.chats.delete_one({'id': chat_id})

db = Database(Config.MONGODB_URL)
