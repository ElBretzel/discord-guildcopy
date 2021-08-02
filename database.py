import sqlite3
import os
from functools import wraps

from cachetools import TTLCache, cached

from const import *


class _DBDecorators:
    # * Private class incluing all database decorators

    @classmethod
    def separator(cls, func):
        # * Create some separation during the steps of the database checking.
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("{:-^30}".format(""))
            func(*args, **kwargs)
            print("{:-^30}".format(""))
        return wrapper

    @classmethod
    def check_db_exist(cls, func):
        # * Check the integrity of the database
        # * If the database dont exist, creates a new one
        # * Rows are empty
        @wraps(func)
        def wrapper(*args, **kwargs):
            # * The first element of the arg variable is the instance of DBManager
            # * The kwargs variable contain db cursor in the 'cursor' key
            
            print("[DB] Connection...")
            if kwargs["cursor"].execute("SELECT name FROM sqlite_master WHERE type='table';").fetchone(): # ? Check if the database is not empty
                print("[DB] Database found!")
            else:
                print("[DB] Database not found...")
                print("[DB] Creation of a new database, it will not be long.")
                DBInstance = args[0] # * Assign the DBManager instance in a variable to easily access to it
                DBInstance._create_main_table
                DBInstance._create_member_table
                DBInstance._create_channel_table
            func(*args, **kwargs)
            print("[DB] Ready!")
        return wrapper
    
    @classmethod
    def auto_commit(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            DBInstance = args[0]
            DBInstance.connexion.commit()
        return wrapper
    

class DBSingletonMeta(type):
    # *  Metaclass Singleton to have a single database connection
    _instance = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance[cls] = instance
        return cls._instance[cls]
        
class DBManager(metaclass=DBSingletonMeta):
    # * Represents the whole class which control the cat database.
    # * The class is a Singleton, each instance return the same class instance.
    
    DB = sqlite3.connect(os.path.join(DIRECTORY, "data.db")) # ? Connection to the cat sqlite3 DB
    
    def __init__(self):
        self._connexion = self.DB
        self._cursor = self.connexion.cursor()
        self.on_db_launch(cursor=self._cursor)            
        
    @property
    def connexion(self):
        return self._connexion
    
    @connexion.setter
    def connexion(self, *args, **kwargs):
        raise AttributeError # ! Avoid user manually create a connection
    
    @property
    def cursor(self):
        return self._cursor
    
    @cursor.setter
    def cursor(self, *args, **kwargs):
        raise AttributeError  # ! Avoid user manually create a cursor
    
    
    @_DBDecorators.separator
    @_DBDecorators.check_db_exist
    @_DBDecorators.auto_commit
    def on_db_launch(self, cursor):
        print("[DB] Initialization...")
        self.cursor.execute("PRAGMA foreign_keys = ON")
    
    @property 
    @_DBDecorators.auto_commit
    def _create_main_table(self) -> None:
        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS main(
                    guild_id INTEGER PRIMARY KEY,
                    channels_id TEXT
                    );
                    """)
        print("[DB] Guild table successfully created!")

    @property
    @_DBDecorators.auto_commit
    def _create_member_table(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS member(
            member_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            edited BOOL NOT NULL DEFAULT false,
            roles TEXT NOT NULL,
            owner BOOL NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES main(guild_id) ON DELETE CASCADE
        );
        """)
        print("[DB] Member table successfully created!")

    @property
    @_DBDecorators.auto_commit
    def _create_channel_table(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel(
            channel_id INTEGER PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            user_perm TEXT NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES main(guild_id) ON DELETE CASCADE
        );
        """)
        print("[DB] Channel table successfully created!")

    @_DBDecorators.auto_commit
    def add_guild(self, guild, channels_id=None):
        self.cursor.execute("""
        INSERT INTO main (guild_id, channels_id)
        VALUES (?, ?);
        """, (guild.id, channels_id))

    @_DBDecorators.auto_commit
    def edit_guild(self, guild, channels_id):
        self.cursor.execute("""
        UPDATE main
        SET channels_id = ?
        WHERE guild_id = ?
        """, (channels_id, guild.id))

    @_DBDecorators.auto_commit
    def add_member(self, member, guild, roles, owner):
        self.cursor.execute("""
        INSERT INTO member (member_id, guild_id, roles, owner)
        VALUES (?, ?, ?, ?);
        """, (member.id, guild.id, roles, owner.id == member.id))

    @_DBDecorators.auto_commit
    def add_channel(self, channel, guild, user_perm):
        self.cursor.execute("""
        INSERT INTO channel (channel_id, guild_id, type, user_perm)
        VALUES (?, ?, ?, ?)
        """, (channel.id, guild.id, channel.type.name, user_perm))

    def get_member(self, member):
        self.cursor.execute("""
        SELECT roles, owner
        FROM member
        INNER JOIN main
        ON main.guild_id = member.guild_id
        WHERE main.guild_id = ? AND member.member_id = ? AND member.edited = false
        ;
        """, (member.guild.id, member.id))

        return self.cursor.fetchone()

    @_DBDecorators.auto_commit
    def member_edited(self, member):
        self.cursor.execute("""
        UPDATE member
        SET edited = true
        WHERE member_id = ? AND guild_id = ?
        """, (member.id, member.guild.id))

    def get_channel_user_perm(self, member):

        self.cursor.execute("""
        SELECT channel_id, user_perm
        FROM channel
        INNER JOIN main
        ON main.guild_id = channel.guild_id
        WHERE main.guild_id = ?
        """, (member.guild.id,))

        return self.cursor.fetchall()

    def fetch_channel(self, guild):
        self.cursor.execute("""
        SELECT channels_id
        FROM main
        WHERE guild_id = ?
        """, (guild.id,))

        return self.cursor.fetchone()


if __name__ == "__main__":
    
    s1 = DBManager()
    s2 = DBManager()
    print(id(s1), id(s2))
