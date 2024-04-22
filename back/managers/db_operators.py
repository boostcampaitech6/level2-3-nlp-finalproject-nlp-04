from pymongo import errors

from managers.mongo_config import collection


async def find_user_by_email(email: str):
    return await collection.find_one({"_id": email})


async def append_to_field(document_id: str, field_name: str, item):
    try:
        updated_info = await collection.update_one(
            {"_id": document_id},
            {"$push": {field_name: item.model_dump()}}
        )
        return updated_info.modified_count == 1
    except errors.PyMongoError as e:
        print(f"An error occurred: {e}")
        return False