from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
# load model, it takes time since it loads over 500 MB model file

import datetime
import pandas as pd
from tqdm import tqdm
import time
import re


def appender(list_to_be_appended, main_list):
    temp_list = list()
    for each in list_to_be_appended:
        temp_list.append(each)
    main_list.append(temp_list)


class WhatsAppAnalytics:
    def __init__(self, dump_file):
        self.main_df = None
        self.dump_file = dump_file
        self.raw_list = []
        self.date_list = []
        self.message_list = []
        self.user_list = []
        self.conversation_list = []
        self.conversation_list_element = []
        self.conversation_delay = 300
        # self.main_df = pd.DataFrame()

        self.reg_split = r'\[([\.\d]+\s[\d\:]+)\]'
        self.reg_date = r'([\.\d]+\s[\d\:]+)'

        self.previous_date = datetime.datetime.now()
        self.first_date = self.previous_date
        self.last_date = self.previous_date
        self.date_checker = self.previous_date

        with open(self.dump_file, "r") as fp:
            self.raw_file = fp.read()
            self.raw_list = re.split(self.reg_split, self.raw_file)
            self.raw_list = [each.replace("\n", " ").strip() for each in self.raw_list]

    def create_df_from_raw(self):
        for i, each in enumerate(self.raw_list[1:]):
            try: 
                if i%2 == 0:
                    each = datetime.datetime.strptime(each, "%d.%m.%Y %H:%M:%S")
                    self.date_list.append(each)
                else:
                    self.message_list.append(each.split(":", 1)[1])
                    self.user_list.append(each.split(":", 1)[0])
            except IndexError:
                print("index error")
                print(each)

        self.main_df = pd.DataFrame(list(zip(self.date_list, self.user_list, self.message_list)), columns=["date", "user", "message"])

    def conversation_finder(self):
        for curr_date in self.main_df["date"]:
            if self.first_date == self.date_checker:
                self.first_date = curr_date
                self.previous_date = curr_date
                self.conversation_list_element.append(self.first_date)
                continue
            difference = curr_date - self.previous_date
            if 0 < difference.total_seconds() < self.conversation_delay:
                continue
            else:
                self.last_date = curr_date
                self.conversation_list_element.append(self.last_date)
            if len(self.conversation_list_element) == 2:
                appender(self.conversation_list_element, self.conversation_list)
                # conversation_list.append(conversation_list_element)
                self.first_date = self.date_checker
                self.conversation_list_element.clear()
            self.previous_date = curr_date
        print(len(self.conversation_list))

    def calculate_sentiment_scores(self):
        model = AutoModelForSequenceClassification.from_pretrained("savasy/bert-base-turkish-sentiment-cased")
        tokenizer = AutoTokenizer.from_pretrained("savasy/bert-base-turkish-sentiment-cased")
        sentiment_list = list()
        # create pipeline
        sa = pipeline("sentiment-analysis", tokenizer=tokenizer, model=model)
        # sentiment_scores = sa(self.main_df["message"].to_list())
        # for each in tqdm(sentiment_scores):
        #     if each['label'] == 'positive':
        #         sentiment_list.append(each['score'])
        #     elif each['label'] == 'negative':
        #         sentiment_list.append(0-each['score'])
        #     else:
        #         print("problem var")

        for each in tqdm(self.main_df["message"]):
            try:
                sentiment_score = sa(each)
                if sentiment_score[0]['label'] == 'positive':
                    sentiment_list.append(sentiment_score[0]['score'])
                elif sentiment_score[0]['label'] == 'negative':
                    sentiment_list.append(0-sentiment_score[0]['score'])
                else:
                    sentiment_list.append("ELSE")
                    print(sentiment_score)
            except RuntimeError:
                print(each)
                sentiment_list.append("NONE")
                continue
        self.main_df["sentiment_scores"] = sentiment_list

        print(self.main_df.tail(200))

    def save_to_excel(self, filename):
        self.main_df.to_excel("{}.xlsx".format(filename))

    def load_from_excel(self, file_name):
        self.main_df = pd.read_excel(file_name, index_col=0)


start_time = time.time()
analyzer = WhatsAppAnalytics("_chat.txt")
analyzer.create_df_from_raw()
analyzer.conversation_finder()
analyzer.calculate_sentiment_scores()
analyzer.save_to_excel("_chat")
print("--- %s seconds ---" % (time.time() - start_time))
