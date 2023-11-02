import redis
import pickle


class RedisClient:
    def __init__(self):
        self.redis = self.get_redis_client()
        pass

    def get_redis_client(self) -> redis.Redis:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        return redis_client

    def serialize_object(self, obj):
        return pickle.dumps(obj)

    def deserialize_object(self, serialized_obj):
        return pickle.loads(serialized_obj)

    def remove_record_by_email(self, email, app_code):
        cursor = 0
        keys_to_remove = []

        while True:
            # Scan for keys matching the pattern (e.g., 'access_token:*')
            cursor, keys = self.redis.scan(cursor=cursor, match='*')
            print(cursor)
            # Iterate over the keys and check if the email matches
            for key in keys:
                record = self.redis.get(key)
                token = self.deserialize_object(record)
                if record and token.email == email and token.app_code == app_code:
                    keys_to_remove.append(key)

            # If the cursor is '0', it means the iteration is finished
            if cursor == 0:
                break

        # Remove the matched keys
        if keys_to_remove:
            self.redis.delete(*keys_to_remove)
