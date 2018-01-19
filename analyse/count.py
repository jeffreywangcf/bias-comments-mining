import MySQLdb as mysql
import os
import jieba
from wordcloud import WordCloud, ImageColorGenerator
from concurrent.futures import ThreadPoolExecutor as tpe
from matplotlib import pyplot as plt


custom_dictionary = ["韩国人", "中国人", "生是中国人", "死是中国魂", "韩国狗", "朝鲜狗", "韩国猪", "猪韩国", "吃狗", "南朝鲜", "大寒冥国", "棒粉" , "小日本"]
filters = set([
    "是不是", "表白", "我", "都", "这个", "这样", "那个", "这么", "还是", "还", "过", "跟", "谁", "说", "觉得", "要", "被", "自己",
    "能", "给", "笑", "知道", "着", "真的", "看", "的", "现在", "为什么", "一个", "没", "比", "来", "有", "是", "把", "打",
    "才", "很", "小", "对", "好", "她", "太", "大", "多", "在", "啊", "哈", "和", "呢", "听", "吧", "吗", "吃", "又", "去",
    "到", "像", "做", "你", "会", "他", "人", "了", "也", "么", "个", "不", "上", "没有", "所以", "我们", "感觉", "感觉",
    "怎么", "弹幕", "就是", "好看", "好吃", "回复", "你们", "但是", "他们", "什么", "不是", "一样", "可以", "时候" , "不要" , "因为"	,
    "还有"	, "前面"	, "不会"	, "那么"	, "楼主"	, "看到"	, "这是"	, "应该"	, "好像"	, "这种"	, "视频"	, "出来"	, "一下"	, "东西"	,
    "不能"	, "厉害"	, "已经"	, "其实"	, "人家"	, "很多"	, "可能"	, "一直"	, "好听"	, "有点"	, "哈哈"	, "声音"	, "如果"	, "这里"	, "大家"	,
    "只是"	, "表示"	, "只有"	, "以为"	, "不错"	, "别人"	, "承包"	, "这些"	, "开始"	, "多少"	, "两个"	, "真是"	, "看看"	, "一点",
    "就" ,"这" ,"想" ,"那" ,"最" ,"用" ,"为" ,"叫" ,"让" ,"呀" ,"真" ,"得" ,"里" ,"啦" ,"啥" ,"一" ,"哦" ,"但" ,"走" ,"更" ,"话" ,
    "买" ,"别" ,"再" ,"挺" ,"年" ,"并" ,"完" ,"只" ,"嘛" ,"请" ,"下" ,"哇" ,"歌" ,"等" ,"拿" ,"超" ,"玩" ,"们" ,"点" ,"钱" ,"前" ,
    "脸" ,"快" ,"懂" ,"高" ,"老" ,"当" ,"黑" ,"问"
])





class CountWords:

    def __init__(self, database, table):
        self.frequency = dict()
        self.file_names = list()
        self.thread_pool_size = 8
        self.var_names = ["word", "frequency"]
        with open("/Users/Excited/localmysqlrootssh.txt", "r")as f:
            local_info = f.readlines()   #host, username, passwd, port
            local_info = list(map(str.strip, local_info))
            try:
                self.connection = mysql.connect(
                    host=local_info[0],
                    user=local_info[1],
                    passwd=local_info[2],
                    db=database,
                    port=int(local_info[3]),
                    charset="utf8"
                )
            except mysql.Error as e:
                print("Error: %s" % e)
        self.cursor = self.connection.cursor()
        self.table = table

    def filter_frequency_with(self, target_filter):
        for item in target_filter:
            if self.frequency[item]:
                self.frequency.pop(item)

    def add_dictionary_from(self, target_dict):
        for item in target_dict:
            jieba.add_word(item)

    def get_all_data_file_name(self):
        abs_path = "/Users/Excited/PycharmProjects/bias_comments/data/"
        for parent_file_name in os.walk(abs_path):
            for child_file_name in parent_file_name[-1]:
                if child_file_name[-4:] == ".txt":
                    self.file_names.append(parent_file_name[0] + child_file_name)
        print("found %d files in total"%len(self.file_names))

    def read_from_file_and_count(self):
        def _read_from_file_and_count(file_name):
            with open(file_name, 'r') as f:
                lines = f.readlines()
                if len(lines) < 10:
                    return
                for line in lines:
                    if not isinstance(line, str) or len(line) < 4 or len(line) > 500:
                        continue
                    vline = self.validate(line)
                    splited_words = [item for item in jieba.cut(vline)]
                    for splited_word in splited_words:
                        self.frequency[splited_word] = self.frequency.get(splited_word, 0) + 1
            self.file_names.remove(file_name)
            print("finish counting %s" % file_name)

        executor = tpe(self.thread_pool_size)
        executor.map(_read_from_file_and_count, self.file_names)
        executor.shutdown(wait=True)



    def validate(self, line):
        length = len(line)
        mark_list = list()
        frontIndex = 0
        endIndex = 1
        while True:
            if endIndex >= length and endIndex - frontIndex < 3:
                break
            if endIndex - frontIndex < 3:
                endIndex += 1
                continue
            if line[frontIndex] == line[frontIndex + 1] == line[frontIndex + 2]:
                currentCharacter = line[frontIndex]
                frontIndex += 1
                while frontIndex < length and line[frontIndex] == currentCharacter:
                    mark_list.append(frontIndex)
                    frontIndex += 1
                endIndex = frontIndex + 1
            else:
                frontIndex += 1
        if len(mark_list) == 0:
            return line.strip()
        unmarked = [i for i in range(length) if i not in mark_list]
        return "".join([line[i] for i in unmarked]).strip()

    def make_wordcloud(self):
        stop_words = {}
        back_coloring_path = 

    def save_frequency_to_sql(self):
        self.frequency = sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)
        for pair in self.frequency:
            self.addRow(pair)

    def closeConnection(self):
        if self.connection:
            self.connection.close()

    def __del__(self):
        self.closeConnection()

    def getFormat(self):
        self.cursor.execute("desc %s"%self.table)
        return self.cursor.fetchall()

    def execute(self, command):
        assert isinstance(command, str)
        self.cursor.execute(command)

    def getOne(self, with_label = False):
        try:
            res = self.cursor.fetchone()
            if not with_label:
                return res
            res_dict = dict(zip([item[0] for item in self.cursor.description], res))
            return res_dict
        except mysql.Error as e:
            print("error: %s"%e)
            self.connection.rollback()
        except:
            print("error")
            self.connection.rollback()

    def getAll(self, with_label = False):
        try:
            res = self.cursor.fetchall()
            if not with_label:
                return res
            res_list = list()
            for row in res:
                res_list.append(dict(zip([item[0] for item in self.cursor.description], row)))
            return res_list
        except mysql.Error as e:
            print("error: %s"%e)
            self.connection.rollback()
        except:
            print("error")
            self.connection.rollback()

    def addRow(self, data):
        try:
            command = "insert into " + self.table + "(" + ", ".join(["`" + str(item) + "`" for item in self.var_names]) + ")"
            command += "VALUE(" + ", ".join(['"' + str(item) + '"' for item in data]) +");"
            self.execute(command)
            self.connection.commit()
        except mysql.Error as e:
            print("error: %s"%e)
            self.connection.rollback()
        except:
            print("error")
            self.connection.rollback()