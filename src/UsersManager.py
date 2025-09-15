import pickle
from multiprocessing import Lock
import os

class UsersManager():
    
    def __init__(self, usersFile = "./resources/users.pkl"):
        self._usersFile = usersFile
        self._lock = Lock()
        # Ensure file exists
        os.makedirs(os.path.dirname(self._usersFile), exist_ok=True)
        if not os.path.exists(self._usersFile):
            with open(self._usersFile, "wb") as f:
                pickle.dump({}, f)
    
    def getKnownUsers(self):
        with self._lock:
            with open(self._usersFile, "rb") as f:
                return pickle.load(f).keys()
        
    def getUser(self, userId):
        with self._lock:
            with open(self._usersFile, "rb") as f:
                user = pickle.load(f)[userId]
            return user
    
    def setUser(self, userId, user):
        with self._lock:
            with open(self._usersFile, "rb") as f:
                options = pickle.load(f)
            options[userId] = user
            with open(self._usersFile, "wb") as f:
                pickle.dump(options, f)
