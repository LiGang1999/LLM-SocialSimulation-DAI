from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax

# Preprocess text (username and link placeholders)


class Sentiment:
    """docstring for Sentiment"""

    def __init__(self):
        super(Sentiment, self).__init__()
        MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.config = AutoConfig.from_pretrained(MODEL)
        # PT
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    def preprocess(self, text):
        new_text = []
        for t in text.split(" "):
            t = "@user" if t.startswith("@") and len(t) > 1 else t
            t = "http" if t.startswith("http") else t
            new_text.append(t)
        return " ".join(new_text)

    def return_sentiment(self, text):
        text = self.preprocess(text)
        encoded_input = self.tokenizer(text, return_tensors="pt")
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        sentiment_str = "The following sentiment analysis results are categorized as Negative, Neutral, and Positive, and the sum of the three labels is 1. "
        for i in range(scores.shape[0]):
            l = self.config.id2label[ranking[i]]
            s = scores[ranking[i]]
            sentiment_str += f"The level of {l} sentiment is {np.round(float(s), 4)}."
            # print(f"{i+1}) {l} {np.round(float(s), 4)}")
        return sentiment_str


# model.save_pretrained(MODEL)
# text = "Covid cases are increasing fast!"
# test = Sentiment()
# print(test.return_sentiment(text))
# base_the_ville_isabella_maria_klaus
# What is your attitude towards nuclear wastewater?
# What is your attitude towards nuclear wastewater discharging into the sea?
#
# 你害怕日本核污染水排海带来的影响吗？
# Are you afraid of the impact of Japan's nuclear contaminated water discharge into the sea?
#
# init dk ###初始化向量数据库###
# call -- load case the_ville/agent_history_init_n3.csv ###广播事件###必须要在run之后执行（找时间处理下）
# call -- run spp ###制定政策###
# call -- release policy the_ville/agent_history_init_n3.csv ###发布政策###
#
# 扩大动作空间；市长竞选案例（“向量数据库”和“情感分析模块”还未使用）。
#
# 1) init dk ###初始化向量数据库###
# 2) run 2 ###初始化###
# 3) call -- load case the_ville/agent_history_init_n3.csv ###广播事件（或者发布已有的政策）###
# 3-1) Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters. ###案例内容###
# 4) call -- run spp ###制定政策###
# 5) call -- release policy the_ville/agent_history_init_n3.csv ###发布政策###
# 6) run 118 ###一共模拟五天，步长为一小时，所以一共120步，由于前面模拟了2步，这里只需要模拟118步###
# 7) call -- analysis {name} ###模拟完开始面试，比如call -- analysis Isabella Rodriguez###
# 7-1) Are you afraid of the impact of Japan's nuclear contaminated water discharge into the sea? ###问题（注意记录输出的答案）###
# 7-2) end_convo ###退出对当前这个人的面试###
# 8) fin ###保存并退出，或者返回7)对下一个智能体进行面试###
#
