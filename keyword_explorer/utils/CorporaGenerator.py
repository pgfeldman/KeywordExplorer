from keyword_explorer.utils.MySqlInterface import MySqlInterface
import tkinter.filedialog as fd
import tkinter.messagebox as message
import random
from datetime import datetime

from typing import Dict, List

class CorporaGenerator:
    tweet_created_at_flag:bool
    language_flag:bool
    exclude_thread_flag:bool
    keyword_flag:bool
    name_flag:bool
    username_flag:bool
    location_flag:bool
    description_flag:bool
    wrap_after_text_flag:bool
    single_file_flag:bool
    percent_on_flag:bool
    excluded_culsters_flag:bool
    msi:MySqlInterface
    directory:str

    def __init__(self, msi:MySqlInterface):
        self.msi = msi
        self.tweet_created_at_flag= False
        self.language_flag= False
        self.exclude_thread_flag = False
        self.keyword_flag= False
        self.name_flag= False
        self.username_flag= False
        self.location_flag= False
        self.description_flag= False
        self.wrap_after_text_flag = True
        self.single_file_flag= False
        self.percent_on_flag = True
        self.excluded_culsters_flag= False
        self.directory = "./"

    def set_by_name(self, name:str) -> bool:
        val:bool = self.__getattribute__(name)
        self.__setattr__(name, (not val))
        val:bool = self.__getattribute__(name)
        print("{} = {}".format(name, val))
        return val

    def set_folder(self):
        self.directory = fd.askdirectory()
        print("set_folder = {}".format(self.directory))

    def get_where_options(self) -> Dict:
        where_options_dict = {}
        if self.excluded_culsters_flag:
            where_options_dict['exclude'] = not self.excluded_culsters_flag
        if self.exclude_thread_flag:
            where_options_dict['is_thread'] = not self.exclude_thread_flag
        return where_options_dict

    def write_files(self, experiment_id:int, keyword:str, limit:int = 0):
        limit_str = ""
        if limit > 0:
            limit_str = "LIMIT {}".format(limit)
        keyword_list = [keyword]
        d:Dict
        if keyword == 'all_keywords':
            sql = "select distinct keywords from twitter_v2.table_experiment where id = %s"
            vals = (experiment_id, )
            result = self.msi.read_data(sql, vals)
            d = result[0]
            s:str = d['keywords']
            keyword_list = s.split(',')

        if self.single_file_flag:
            sql = 'select * from tweet_user_cluster_view where experiment_id = %s '
            where_options_dict = self.get_where_options()
            vals = [experiment_id, ]
            for key, val in where_options_dict.items():
                sql = "{}and {} = %s ".format(sql, key)
                vals.append(val)
            sql += limit_str
            result = self.msi.read_data(sql, tuple(vals))
            self.write_keyword_file('all_keywords', result)
            print("\n-------\n{}\n{}".format(sql, tuple(vals)))
            message.showinfo("Corpora", "Test/Train files written for all keywords")
            return

        keyword:str
        for keyword in keyword_list:
            print("\n---------{}".format(keyword))
            sql = 'select * from tweet_user_cluster_view where experiment_id = %s and keyword = %s '
            where_options_dict = self.get_where_options()
            vals = [experiment_id, keyword.strip()]
            for key, val in where_options_dict.items():
                sql = "{}and {} = %s ".format(sql, key)
                vals.append(val)
            sql += limit_str
            result = self.msi.read_data(sql, tuple(vals))
            self.write_keyword_file(keyword, result)
            print("\n-------\n{}\n{}".format(sql, tuple(vals)))
            # for d in result:
            #     print(d)
        message.showinfo("Corpora", "Test/Train files written for {}".format(keyword_list))

    def write_keyword_file(self, keyword:str, query_result_list:List, test_percent:float = 0.2):
        print("{}: writing {} rows".format(keyword, len(query_result_list)))
        probs = {"ten":0.1, "twenty":0.3, "thirty":0.6, "forty":1.0}
        date_fmt = "%b-%d-%Y_%H-%M-%S"
        now = datetime.now()
        d:Dict
        test_f = open("{}/{}_test_{}.txt".format(self.directory, keyword, now.strftime(date_fmt)), mode='w', encoding='utf-8')
        train_f = open("{}/{}_train_{}.txt".format(self.directory, keyword, now.strftime(date_fmt)), mode='w', encoding='utf-8')

        for d in query_result_list:
            meta_dict = {}
            if self.tweet_created_at_flag:
                meta_dict['created'] = d['created_at']
            if self.language_flag:
                meta_dict['language'] = d['lang']
            if self.keyword_flag:
                meta_dict['keyword'] = keyword
            if self.name_flag:
                meta_dict['name'] = d['name']
            if self.username_flag:
                meta_dict['username'] = d['username']
            if self.location_flag:
                meta_dict['location'] = d['location']
            if self.description_flag:
                meta_dict['description'] = d['description']
            if self.percent_on_flag:
                prob = random.random()
                for key, val in probs.items():
                    if prob <= val:
                        meta_dict['probability'] = key
                        break

            cleaned_str = d['text'].replace("\n", "")
            s = "text: {}".format(cleaned_str)
            if self.wrap_after_text_flag:
                for key, val in meta_dict.items():
                    s = "{} || {}: {}".format(s, key, val)
            else:
                for key, val in meta_dict:
                    s = "{}: {} || {}".format(key, val, s)


            #if self.wrap_after_text_flag:
            if random.random() < test_percent:
                test_f.write("[[{}]]\n".format(s))
            else:
                train_f.write("[[{}]]\n".format(s))

        test_f.flush()
        test_f.close()
        train_f.flush()
        train_f.close()


def main():
    msi = MySqlInterface(user_name="root", db_name="twitter_v2")
    cg = CorporaGenerator(msi)

    cg.tweet_created_at_flag= True
    cg.language_flag= True
    cg.keyword_flag= True
    cg.name_flag= True
    cg.username_flag= True
    cg.location_flag= True
    cg.description_flag= True
    cg.wrap_after_text_flag = True
    cg.single_file_flag= True
    cg.percent_on_flag = True
    cg.excluded_culsters_flag= True
    cg.exclude_thread_flag= True

    cg.set_folder()
    # cg.write_files(1, "paxlovid OR Nirmatrelvir OR ritonavir")
    cg.write_files(1, "all_keywords", limit=10)

if __name__ == "__main__":
    main()
