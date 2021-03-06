try:
    import ujson as json
except ImportError:
    import json

import irc3
from pathlib import Path


@irc3.plugin
class UserDB(dict):

    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)

        self.__bot = bot
        self.__root = Path('data')
        self.__file = self.__root / 'userdb.json'

        try:
            with self.__file.open('r') as fd:
                self.update(json.load(fd))
        except FileNotFoundError:
            # Database file itself doesn't need to exist on first run, it will be created on first write.
            if not self.__file.exists():
                # Copy ricedb.json from old installations if it exists.
                old_db_file = Path(self.__root) / 'ricedb.json'
                if old_db_file.exists():
                    old_db_file.replace(self.__file)
                    with self.__file.open('r') as fd:
                        self.update(json.load(fd))
                else:
                    self.__root.mkdir(exist_ok=True)
                    self.__file.touch(exist_ok=True)
                    self.__bot.log.debug(f'Created {self.__root} directory')

    @irc3.extend
    def get_user_value(self, username: str, key: str):
        try:
            return self.get(username)[key]
        except (KeyError, TypeError):
            return None

    @irc3.extend
    def del_user_value(self, username: str, key: str):
        try:
            del self[username][key]
        except KeyError:
            pass
        with self.__file.open('w') as fd:
            json.dump(self, fd)

    @irc3.extend
    def set_user_value(self, username: str, key: str, value):
        data = {key: value}
        try:
            self[username].update(data)
        except KeyError:
            self[username] = data
        with self.__file.open('w') as fd:
            json.dump(self, fd)
