from firebase_admin import credentials, firestore
import firebase_admin
import hashlib

class CloudDatabaseManger:
    def __init__(self) -> None:
        path = r"/Users/damolaolugboji/Desktop/code/luna-backend/database/moodstream-e1c4f-firebase-adminsdk-1dlhj-220576a4d5.json"
        cred = credentials.Certificate(path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self.database = firestore.client()
        
    def store_data_firestore(self,keyword, collection_name, data):
        query_hash = hashlib.md5(keyword.encode("utf-8")).hexdigest()
        doc_ref = self.database.collection(collection_name).document(query_hash)
        doc_ref.set(data)
    
    # def get_cached_articles(self, keyword, collection_name):
    #     query_hash = hashlib.md5(keyword.encode("utf-8")).hexdigest()
    #     doc_ref = self.database.collection(collection_name).document(query_hash)
    #     doc = doc_ref.get()

    #     if doc.exists:
    #         return doc.to_dict()["data"]
    #     else:
    #         return None