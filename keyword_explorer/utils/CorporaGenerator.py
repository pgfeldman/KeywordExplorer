from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.tkUtils.Checkboxes import Checkboxes
import os

class CorporaGenerator:
    meta_wrapping_flag:bool
    tweet_created_at_flag:bool
    language_flag:bool
    keyword_flag:bool
    author_flag:bool
    name_flag:bool
    username_flag:bool
    location_flag:bool
    description_flag:bool
    wrap_after_text_flag:bool
    single_file_flag:bool
    percent_on_flag:bool
    excluded_culsters_flag:bool
    msi:MySqlInterface

    def __init__(self, msi:MySqlInterface):
        self.msi = msi
        self.meta_wrapping_flag =  False
        self.tweet_created_at_flag =  False
        self.language_flag =  False
        self.keyword_flag =  False
        self.author_flag =  False
        self.name_flag =  False
        self.username_flag =  False
        self.location_flag =  False
        self.description_flag =  False
        self.wrap_after_text_flag =  True
        self.single_file_flag =  False
        self.percent_on_flag =  True
        self.excluded_culsters_flag =  False

    def set_by_name(self, name:str) -> bool:
        val:bool = self.__getattribute__(name)
        self.__setattr__(name, (not val))
        val:bool = self.__getattribute__(name)
        print("{} = {}".format(name, val))
        return val


