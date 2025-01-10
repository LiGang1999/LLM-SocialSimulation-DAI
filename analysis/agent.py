import pandas as pd
import os
from datetime import datetime
from openai import OpenAI
import numpy as np
from collections import Counter
import time
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Set, TYPE_CHECKING
from enum import Enum
import logging


# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

if TYPE_CHECKING:
    from typing import Type
    from openai import OpenAI


@dataclass
class SpeechContext:
    meeting_type: str
    date: datetime
    topic: str
    background: Optional[str] = None
    related_bills: Optional[List[str]] = None
    current_stage: Optional[str] = None
    previous_speeches: List[Dict] = field(default_factory=list)
    current_mood: Optional[str] = None
    time_limit: Optional[int] = None


class SpeechType(Enum):
    MOTION = "动议"
    QUESTION = "质询"
    DEBATE = "辩论"
    COMMENT = "评论"
    OTHER = "其他"


@dataclass
class SpeechQuality:
    relevance: float
    coherence: float
    persuasiveness: float
    professionalism: float

    def get_overall_score(self) -> float:
        weights = {
            "relevance": 0.3,
            "coherence": 0.2,
            "persuasiveness": 0.3,
            "professionalism": 0.2,
        }
        return sum(getattr(self, attr) * weight for attr, weight in weights.items())


class SimpleTokenizer:
    def __init__(self):
        # 扩展停用词列表
        self.stop_words = set(
            [
                "的",
                "了",
                "在",
                "是",
                "我",
                "有",
                "和",
                "就",
                "都",
                "而",
                "及",
                "与",
                "这",
                "那",
                "但",
                "又",
                "或",
                "如",
                "若",
                "则",
                "此",
                "因",
                "个",
                "之",
                "以",
                "到",
                "并",
                "等",
                "着",
                "被",
                "让",
                "往",
                "向",
                "从",
                "给",
                "对",
                "为",
                "由",
                "将",
                "要",
            ]
        )

        # 添加立法会特定的停用词
        self.legislative_stop_words = set(
            [
                "主席",
                "议员",
                "本人",
                "政府",
                "当局",
                "立法会",
                "委员会",
                "司长",
                "先生",
                "女士",
            ]
        )

        # 添加标点符号
        self.punctuation = set(
            ["，", "。", "！", "？", "；", "：", '"', '"', """, """, "、", "（", "）"]
        )

    def cut(self, text: str) -> List[str]:
        """将文本分词，支持中文分词"""
        text = self._clean_text(text)
        words = []
        current_word = ""

        for char in text:
            if char in self.punctuation or char.isspace():
                if current_word:
                    words.append(current_word)
                    current_word = ""
            else:
                current_word += char

        if current_word:
            words.append(current_word)

        words = [
            w
            for w in words
            if w and w not in self.stop_words and w not in self.legislative_stop_words
        ]
        return words

    def _clean_text(self, text: str) -> str:
        """清理文本，去除特殊字符和规范化空白"""
        text = self._full_to_half(text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：""' "、（）]", "", text)
        return text.strip()

    def _full_to_half(self, text: str) -> str:
        """将全角字符转换为半角字符"""
        full = '，。！？；：""' "、（）"
        half = ",.!?;:\"\"'',()"
        trans_dict = dict(zip(full, half))
        return "".join(trans_dict.get(c, c) for c in text)

    def get_word_frequency(self, text: str, top_n: int = 10) -> Dict[str, int]:
        """获取文本中词语的频率统计"""
        words = self.cut(text)
        word_freq = Counter(words)
        return dict(word_freq.most_common(top_n))

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """提取文本中的关键词"""
        word_freq = self.get_word_frequency(text, top_n=top_n)
        return list(word_freq.keys())

    def find_legislative_terms(self, text: str) -> List[str]:
        """识别立法相关的专业术语"""
        legislative_terms = set(
            [
                "条例",
                "法案",
                "修订",
                "草案",
                "附表",
                "条文",
                "规例",
                "决议",
                "动议",
                "委员会",
                "表决",
                "投票",
                "辩论",
                "质询",
                "答复",
            ]
        )

        words = self.cut(text)
        return [w for w in words if any(term in w for term in legislative_terms)]


class SpeechTypeClassifier:
    def __init__(self):
        self.type_patterns = {
            SpeechType.MOTION: {
                "keywords": ["动议", "提出", "建议", "要求", "促请"],
                "patterns": [r"本人提出.*动议", r"动议.*通过", r"现动议.*"],
            },
            SpeechType.QUESTION: {
                "keywords": ["质询", "提问", "询问", "请问", "要求解释"],
                "patterns": [
                    r"(?:想|要|必须)(?:问|了解|知道).*？",
                    r"(?:请|望|希望).*(?:告知|解释|说明).*？",
                    r"(?:是否|如何|为何|为什么).*？",
                ],
            },
            SpeechType.DEBATE: {
                "keywords": ["反对", "支持", "赞成", "认为", "辩论"],
                "patterns": [
                    r"本人(?:反对|支持|赞成)",
                    r"(?:不能|必须)同意",
                    r"对此.*(?:有不同意见|表示关注)",
                ],
            },
            SpeechType.COMMENT: {
                "keywords": ["评论", "意见", "看法", "观点", "回应"],
                "patterns": [
                    r"就.*(?:发表意见|作出评论)",
                    r"本人认为",
                    r"对此.*(?:有以下看法|表示关注)",
                ],
            },
        }

    def classify(self, text: str) -> SpeechType:
        scores = {speech_type: 0 for speech_type in SpeechType}

        for speech_type, patterns in self.type_patterns.items():
            # 关键词匹配
            for keyword in patterns["keywords"]:
                if keyword in text:
                    scores[speech_type] += 1

            # 正则表达式匹配
            for pattern in patterns["patterns"]:
                if re.search(pattern, text):
                    scores[speech_type] += 2

        # 如果没有明显特征，归类为其他
        max_score = max(scores.values())
        if max_score == 0:
            return SpeechType.OTHER

        # 返回得分最高的类型
        return max(scores.items(), key=lambda x: x[1])[0]


class SpeechQualityEvaluator:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client

    def evaluate(
        self, speech: str, context: SpeechContext, profile: Dict
    ) -> SpeechQuality:
        """评估发言质量"""
        prompt = self._build_evaluation_prompt(speech, context, profile)

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的立法会发言评估专家，请根据以下维度评估发言质量：\n"
                        "1. 相关性（0-1）：发言与主题的相关程度\n"
                        "2. 连贯性（0-1）：论述的逻辑性和连贯性\n"
                        "3. 说服力（0-1）：论据的充分性和说服力\n"
                        "4. 专业性（0-1）：专业知识的运用程度",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.3,
                max_tokens=500,
            )

            # 解析评分结果
            result = self._parse_evaluation_response(
                response.choices[0].message.content
            )
            return SpeechQuality(**result)

        except Exception as e:
            print(f"评估发言质量时出错: {str(e)}")
            return SpeechQuality(
                relevance=0.5, coherence=0.5, persuasiveness=0.5, professionalism=0.5
            )

    def _build_evaluation_prompt(
        self, speech: str, context: SpeechContext, profile: Dict
    ) -> str:
        return f"""请评估以下立法会发言：

发言背景：
- 会议类型：{context.meeting_type}
- 讨论主题：{context.topic}
- 当前阶段：{context.current_stage or '一般讨论'}

议员背景：
- 政治立场：{profile.get('political_stance', {}).get('general_stance', '未知')}
- 专业领域：{', '.join(profile.get('expertise_areas', {}).get('primary_areas', ['未知']))}

发言内容：
{speech}

请从相关性、连贯性、说服力和专业性四个维度进行评分（0-1），并简要说明理由。
格式要求：每个维度一行，分数在前，理由在后，以分号分隔。"""

    def _parse_evaluation_response(self, response: str) -> Dict[str, float]:
        """解析评估响应"""
        scores = {
            "relevance": 0.5,
            "coherence": 0.5,
            "persuasiveness": 0.5,
            "professionalism": 0.5,
        }

        try:
            lines = response.strip().split("\n")
            for line in lines:
                for metric in scores.keys():
                    if metric in line.lower():
                        score_str = re.search(r"(\d+\.?\d*)", line)
                        if score_str:
                            scores[metric] = float(score_str.group(1))
        except Exception as e:
            print(f"解析评估结果时出错: {str(e)}")

        return scores


class LegislatorAgent:
    def __init__(self, profile: Dict, openai_client: OpenAI):
        self.profile = profile
        self.client = openai_client
        self.conversation_history = []
        self.speech_quality_evaluator = SpeechQualityEvaluator(self.client)

    def generate_speech(self, context: SpeechContext) -> str:
        prompt = self._build_generation_prompt(context)

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.7,
                max_tokens=1500,
            )

            generated_speech = response.choices[0].message.content

            # 评估发言质量
            quality = self.speech_quality_evaluator.evaluate(
                generated_speech, context, self.profile
            )

            self.conversation_history.append(
                {
                    "context": context,
                    "speech": generated_speech,
                    "quality": quality,
                    "timestamp": datetime.now(),
                }
            )

            return generated_speech

        except Exception as e:
            print(f"生成发言时出错: {str(e)}")
            return ""

    def _build_generation_prompt(self, context: SpeechContext) -> str:
        """构建发言生成提示"""
        prompt = f"""请根据以下要求生成一段立法会发言：

    1. 发言背景：
    - 会议类型：{context.meeting_type}
    - 讨论主题：{context.topic}
    - 相关法案：{', '.join(context.related_bills) if context.related_bills else '无'}
    - 当前阶段：{context.current_stage or '一般讨论'}

    2. 发言要求：
    - 使用正式的立法会用语
    - 避免口语化表达
    - 保持简洁明了
    - 突出重点论据
    - 时间限制：{context.time_limit}分钟

    3. 发言结构：
    - 开场：简短的立场说明
    - 主体：2-3个关键论点
    - 结束：明确的建议或要求

    4. 议员特征：
    - 立场：{self.profile['political_stance']['general_stance']}
    - 专业领域：{', '.join(self.profile['expertise_areas']['primary_areas'])}"""

        if context.previous_speeches:
            prompt += "\n\n5. 需要回应的观点："
            for prev_speech in context.previous_speeches[-2:]:  # 只关注最近的2个发言
                prompt += f"\n- {prev_speech['speaker']}: {prev_speech['content']}"

        return prompt

    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        return f"""你是立法会议员{self.profile['basic_info']['name']}。请注意：

    1. 使用立法会标准用语：
    - 称谓：主席、议员
    - 开场：本人就/现就...发言
    - 结束：请主席考虑/促请政府...

    2. 保持以下特征：
    - 政治立场：{self.profile['political_stance']['general_stance']}
    - 专业领域：{', '.join(self.profile['expertise_areas']['primary_areas'])}
    - 论证风格：{self.profile['speech_patterns']['qualitative_analysis']['argument_patterns']}

    3. 发言规范：
    - 严格遵守时限
    - 直接切入主题
    - 避免重复内容
    - 使用准确的专业术语"""

    def _format_political_stance(self) -> str:
        stance = self.profile["political_stance"]
        return f"""总体立场：{stance['general_stance']}
核心价值观：{', '.join(stance['core_values'])}
主要议题立场：{', '.join(f'{k}: {v}' for k, v in stance['issue_positions'].items())}
立场一致性：{stance['consistency']}"""

    def _format_expertise_areas(self) -> str:
        expertise = self.profile["expertise_areas"]
        return f"""主要领域：{', '.join(expertise['primary_areas'])}
知识深度：{expertise['knowledge_depth']}
跨领域能力：{expertise['cross_domain']}
专业术语：{', '.join(expertise['technical_terms'][:5])}"""

    def _format_speech_style(self) -> str:
        style = self.profile["speech_patterns"]["qualitative_analysis"]
        return f"""语言风格：{style['language_style']}
论证方式：{style['argument_patterns']}
互动特点：{style['interaction_style']}
情感表达：{style['emotional_expression']}"""


class LegislatorAnalyzer:
    def __init__(self, csv_path: str, api_key: str = None, base_url: str = None):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        try:
            self.df = pd.read_csv(csv_path)
            self.client = OpenAI(
                api_key=api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=base_url if base_url else None,
            )
            self.profile_cache = {}
            self.tokenizer = SimpleTokenizer()
            self.speech_classifier = SpeechTypeClassifier()
            self.nlp_patterns = self._initialize_nlp_patterns()

            # 添加发言类型分类
            self._classify_speech_types()

            self.logger.info("LegislatorAnalyzer 初始化成功")

        except Exception as e:
            self.logger.error(f"初始化 LegislatorAnalyzer 时出错: {str(e)}")
            raise

    def _initialize_nlp_patterns(self) -> Dict:
        return {
            "formal_words": set(["本人", "本席", "议员", "政府", "当局"]),
            "stance_words": {
                "support": set(["支持", "赞成", "同意", "认可"]),
                "oppose": set(["反对", "否决", "不同意", "质疑"]),
                "neutral": set(["建议", "考虑", "研究", "探讨"]),
            },
            "emotion_words": {
                "strong": set(["必须", "一定", "绝对", "坚决"]),
                "moderate": set(["或许", "可能", "建议", "希望"]),
            },
        }

    def _classify_speech_types(self):
        """对所有发言进行类型分类"""
        self.df["SpeechType"] = self.df["Speeches"].apply(
            lambda x: self.speech_classifier.classify(str(x)).value
        )

    def analyze_legislator(self, member_name: str) -> Dict:
        speeches_df = self.extract_member_speeches(member_name)
        if speeches_df.empty:
            return {"error": f"未找到议员 {member_name} 的发言记录"}

        try:
            profile = {
                "basic_info": self._analyze_basic_info(speeches_df, member_name),
                "speech_patterns": self._analyze_speech_patterns(speeches_df),
                "political_stance": self._analyze_political_stance(speeches_df),
                "expertise_areas": self._analyze_expertise(speeches_df),
                "speech_type_distribution": self._analyze_speech_type_distribution(
                    speeches_df
                ),
                "interaction_patterns": self._analyze_interactions(speeches_df),
            }
            self.profile_cache[member_name] = profile
            return profile
        except Exception as e:
            return {"error": f"分析过程出错: {str(e)}"}

    def _analyze_basic_info(self, speeches_df: pd.DataFrame, member_name: str) -> Dict:
        return {
            "name": member_name,
            "active_period": {
                "start": speeches_df["MeetingDate"].min(),
                "end": speeches_df["MeetingDate"].max(),
            },
            "total_speeches": len(speeches_df),
            "speech_types": speeches_df["SpeechType"].value_counts().to_dict(),
        }

    def _analyze_speech_patterns(self, speeches_df: pd.DataFrame) -> Dict:
        speeches = speeches_df["Speeches"].astype(str).tolist()
        combined_text = " ".join(speeches)

        pattern_prompt = """分析议员的发言模式，包括：
        1. 语言风格（正式/口语，专业术语使用等）
        2. 论证方式（逻辑结构，论据使用等）
        3. 互动特点（回应方式，质询风格等）
        4. 情感表达（语气强度，态度倾向等）
        """

        pattern_analysis = self._call_gpt_api(
            pattern_prompt + f"\n发言样本：\n{' '.join(speeches[:5])}"
        )

        return {
            "qualitative_analysis": {
                "language_style": self._extract_language_style(pattern_analysis),
                "argument_patterns": self._extract_argument_patterns(pattern_analysis),
                "interaction_style": self._extract_interaction_style(pattern_analysis),
                "emotional_expression": self._extract_emotional_patterns(
                    pattern_analysis
                ),
            },
            "quantitative_analysis": {
                "avg_length": np.mean([len(s) for s in speeches]),
                "keywords": self.tokenizer.extract_keywords(combined_text),
                "legislative_terms": self.tokenizer.find_legislative_terms(
                    combined_text
                ),
                "word_frequency": self.tokenizer.get_word_frequency(combined_text),
                "stance_distribution": self._analyze_stance_distribution(speeches),
            },
        }

    def _analyze_political_stance(self, speeches_df: pd.DataFrame) -> Dict:
        speeches = speeches_df["Speeches"].astype(str).tolist()
        stance_prompt = """分析议员的政治立场，包括：
        1. 总体政治倾向
        2. 核心价值观
        3. 对主要议题的态度
        4. 立场的一致性和演变
        """

        stance_analysis = self._call_gpt_api(
            stance_prompt + f"\n发言样本：\n{' '.join(speeches[:5])}"
        )

        return {
            "general_stance": self._extract_general_stance(stance_analysis),
            "core_values": self._extract_core_values(stance_analysis),
            "issue_positions": self._extract_issue_positions(stance_analysis),
            "consistency": self._evaluate_stance_consistency(speeches),
        }

    def _analyze_expertise(self, speeches_df: pd.DataFrame) -> Dict:
        speeches = speeches_df["Speeches"].astype(str).tolist()
        expertise_prompt = """分析议员的专业领域和知识背景，包括：
        1. 主要专业领域
        2. 专业知识深度
        3. 跨领域连接能力
        4. 技术术语使用情况
        """

        expertise_analysis = self._call_gpt_api(
            expertise_prompt + f"\n发言样本：\n{' '.join(speeches[:5])}"
        )

        return {
            "primary_areas": self._extract_primary_areas(expertise_analysis),
            "knowledge_depth": self._extract_knowledge_depth(expertise_analysis),
            "cross_domain": self._extract_cross_domain(expertise_analysis),
            "technical_terms": self._analyze_technical_terms(speeches),
        }

    def _analyze_speech_type_distribution(self, speeches_df: pd.DataFrame) -> Dict:
        type_counts = speeches_df["SpeechType"].value_counts()
        total = len(speeches_df)
        return {
            "type_distribution": {
                speech_type: count / total for speech_type, count in type_counts.items()
            },
            "most_frequent_type": type_counts.index[0],
            "type_counts": type_counts.to_dict(),
        }

    def _analyze_interactions(self, speeches_df: pd.DataFrame) -> Dict:
        """分析议员的互动模式"""
        try:
            speeches = speeches_df["Speeches"].astype(str).tolist()
            interaction_prompt = """分析议员的互动模式，包括：
            1. 回应其他议员的方式
            2. 引用和参考模式
            3. 打断和插话特征
            4. 与主席的互动方式
            """

            interaction_analysis = self._call_gpt_api(
                interaction_prompt + f"\n发言样本：\n{' '.join(speeches[:5])}"
            )

            return {
                "response_patterns": self._extract_response_patterns(
                    interaction_analysis
                ),
                "reference_patterns": self._extract_reference_patterns(
                    interaction_analysis
                ),
                "interruption_patterns": self._extract_interruption_patterns(
                    interaction_analysis
                ),
                "chair_interaction": self._extract_chair_interaction(
                    interaction_analysis
                ),
            }
        except Exception as e:
            self.logger.error(f"分析互动模式时出错: {str(e)}")
            return {
                "response_patterns": {
                    "opening_statements": [],
                    "responses": [],
                    "closing_remarks": [],
                },
                "reference_patterns": [],
                "interruption_patterns": [],
                "chair_interaction": [],
            }

    def generate_speech_agent(self, member_name: str) -> LegislatorAgent:
        """
        为指定议员生成智能体
        """
        try:
            # 获取或生成议员档案
            if member_name in self.profile_cache:
                profile = self.profile_cache[member_name]
            else:
                profile = self.analyze_legislator(member_name)
                self.profile_cache[member_name] = profile

            # 检查是否有错误
            if "error" in profile:
                raise ValueError(f"生成议员档案时出错: {profile['error']}")

            # 创建并返回议员智能体
            return LegislatorAgent(profile=profile, openai_client=self.client)

        except Exception as e:
            print(f"生成议员智能体时出错: {str(e)}")
            raise e

    def extract_member_speeches(self, member_name: str) -> pd.DataFrame:
        """
        提取指定议员的所有发言记录

        Args:
            member_name: 议员姓名

        Returns:
            包含该议员所有发言的DataFrame
        """
        try:
            # 确保数据框中有 'SpeakerName' 列
            if "SpeakerName" not in self.df.columns:
                raise ValueError("CSV文件中缺少 'SpeakerName' 列")

            # 提取该议员的所有发言
            member_speeches = self.df[self.df["SpeakerName"] == member_name].copy()

            # 检查是否找到发言记录
            if member_speeches.empty:
                print(f"警告: 未找到议员 {member_name} 的发言记录")
                return pd.DataFrame()

            # 确保日期列是日期类型
            if "MeetingDate" in member_speeches.columns:
                member_speeches["MeetingDate"] = pd.to_datetime(
                    member_speeches["MeetingDate"], format="%Y-%m-%d", errors="coerce"
                )

            # 按日期排序
            if "MeetingDate" in member_speeches.columns:
                member_speeches = member_speeches.sort_values("MeetingDate")

            # 重置索引
            member_speeches = member_speeches.reset_index(drop=True)

            return member_speeches

        except Exception as e:
            print(f"提取议员发言记录时出错: {str(e)}")
            return pd.DataFrame()

    def _call_gpt_api(self, prompt: str) -> str:
        """
        调用GPT API进行文本分析
        """
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "你是一位专业的立法会发言分析专家。"},
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"调用GPT API时出错: {str(e)}")
            return ""

    def _extract_language_style(self, analysis: str) -> str:
        """从分析结果中提取语言风格"""
        try:
            # 使用GPT分析语言风格
            prompt = f"请从以下分析中提取语言风格的关键特征：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能分析语言风格"

    def _extract_argument_patterns(self, analysis: str) -> str:
        """从分析结果中提取论证模式"""
        try:
            prompt = f"请从以下分析中提取论证方式的主要特点：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能分析论证模式"

    def _extract_interaction_style(self, analysis: str) -> str:
        """从分析结果中提取互动风格"""
        try:
            prompt = f"请从以下分析中提取互动方式的特征：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能分析互动风格"

    def _extract_emotional_patterns(self, analysis: str) -> str:
        """从分析结果中提取情感表达模式"""
        try:
            prompt = f"请从以下分析中提取情感表达的特点：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能分析情感模式"

    def _analyze_stance_distribution(self, speeches: List[str]) -> Dict[str, float]:
        """
        分析发言中的立场分布
        """
        try:
            stance_words = {
                "支持": ["支持", "赞成", "同意", "认可", "赞同"],
                "反对": ["反对", "否决", "不同意", "质疑", "批评"],
                "中立": ["建议", "考虑", "研究", "探讨", "商讨"],
            }

            stance_counts = {stance: 0 for stance in stance_words.keys()}
            total_matches = 0

            # 统计每个立场相关词的出现次数
            for speech in speeches:
                for stance, words in stance_words.items():
                    for word in words:
                        count = speech.count(word)
                        stance_counts[stance] += count
                        total_matches += count

            # 计算分布比例
            if total_matches > 0:
                distribution = {
                    stance: count / total_matches
                    for stance, count in stance_counts.items()
                }
            else:
                distribution = {stance: 0.0 for stance in stance_words.keys()}

            return distribution

        except Exception as e:
            print(f"分析立场分布时出错: {str(e)}")
            return {"支持": 0.0, "反对": 0.0, "中立": 0.0}

    def _extract_general_stance(self, analysis: str) -> str:
        """提取总体政治立场"""
        try:
            prompt = f"请从以下分析中提取议员的总体政治立场：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能确定政治立场"

    def _extract_core_values(self, analysis: str) -> List[str]:
        """提取核心价值观"""
        try:
            prompt = f"请从以下分析中提取议员的核心价值观（以列表形式）：\n{analysis}"
            response = self._call_gpt_api(prompt)
            values = [v.strip() for v in response.split("\n") if v.strip()]
            return values[:5]  # 返回最多5个核心价值观
        except Exception as e:
            return ["未能确定核心价值观"]

    def _extract_issue_positions(self, analysis: str) -> Dict[str, str]:
        """提取对主要议题的立场"""
        try:
            prompt = f"请从以下分析中提取议员对主要议题的立场（以'议题：立场'的形式）：\n{analysis}"
            response = self._call_gpt_api(prompt)
            positions = {}
            for line in response.split("\n"):
                if ":" in line:
                    issue, stance = line.split(":", 1)
                    positions[issue.strip()] = stance.strip()
            return positions
        except Exception as e:
            return {"未能确定": "立场不明"}

    def _evaluate_stance_consistency(self, speeches: List[str]) -> str:
        """评估立场的一致性"""
        try:
            # 分析不同时期的立场分布
            speech_chunks = [
                speeches[i : i + len(speeches) // 3]
                for i in range(0, len(speeches), len(speeches) // 3)
            ]
            distributions = [
                self._analyze_stance_distribution(chunk) for chunk in speech_chunks
            ]

            # 计算立场变化
            variance = np.var([list(d.values()) for d in distributions], axis=0)
            avg_variance = np.mean(variance)

            if avg_variance < 0.1:
                return "高度一致"
            elif avg_variance < 0.2:
                return "基本一致"
            else:
                return "立场有变化"

        except Exception as e:
            return "未能评估一致性"

    def _extract_primary_areas(self, analysis: str) -> List[str]:
        """提取主要专业领域"""
        try:
            prompt = f"请从以下分析中提取议员的主要专业领域（以列表形式）：\n{analysis}"
            response = self._call_gpt_api(prompt)
            areas = [a.strip() for a in response.split("\n") if a.strip()]
            return areas[:3]  # 返回最多3个主要领域
        except Exception as e:
            return ["未能确定专业领域"]

    def _extract_knowledge_depth(self, analysis: str) -> str:
        """评估专业知识深度"""
        try:
            prompt = f"请评估议员在专业领域的知识深度：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能评估知识深度"

    def _extract_cross_domain(self, analysis: str) -> str:
        """评估跨领域能力"""
        try:
            prompt = f"请评估议员的跨领域知识连接能力：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return response.strip()
        except Exception as e:
            return "未能评估跨领域能力"

    def _analyze_technical_terms(self, speeches: List[str]) -> List[str]:
        """分析专业术语使用"""
        try:
            combined_text = " ".join(speeches)
            return self.tokenizer.find_legislative_terms(combined_text)
        except Exception as e:
            return ["未能分析专业术语"]

    def _extract_response_patterns(self, analysis: str) -> Dict[str, List[str]]:
        """提取议员发言的回应模式

        Args:
            analysis: GPT分析的文本结果

        Returns:
            Dict: 包含不同类型回应模式的字典
        """
        try:
            patterns = {
                "opening_statements": [],
                "responses": [],
                "closing_remarks": [],
            }

            # 使用GPT分析文本中的回应模式
            prompt = f"请从以下分析中提取议员的发言开场、回应和结束语模式：\n{analysis}"
            response = self._call_gpt_api(prompt)

            # 解析响应
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("开场"):
                    patterns["opening_statements"].append(line)
                elif line.startswith("回应"):
                    patterns["responses"].append(line)
                elif line.startswith("结束"):
                    patterns["closing_remarks"].append(line)

            return patterns

        except Exception as e:
            self.logger.error(f"提取回应模式时出错: {str(e)}")
            return {
                "opening_statements": ["未能分析开场方式"],
                "responses": ["未能分析回应方式"],
                "closing_remarks": ["未能分析结束语方式"],
            }

    def _extract_reference_patterns(self, analysis: str) -> List[str]:
        """提取引用和参考模式"""
        try:
            prompt = f"请从以下分析中提取议员的引用和参考模式：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return [p.strip() for p in response.split("\n") if p.strip()]
        except Exception as e:
            return ["未能分析引用模式"]

    def _extract_interruption_patterns(self, analysis: str) -> List[str]:
        """提取打断和插话特征"""
        try:
            prompt = f"请从以下分析中提取议员的打断和插话特征：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return [p.strip() for p in response.split("\n") if p.strip()]
        except Exception as e:
            self.logger.error(f"提取打断特征时出错: {str(e)}")
            return ["未能分析打断特征"]

    def _extract_chair_interaction(self, analysis: str) -> List[str]:
        """提取与主席的互动方式"""
        try:
            prompt = f"请从以下分析中提取议员与主席的互动方式：\n{analysis}"
            response = self._call_gpt_api(prompt)
            return [p.strip() for p in response.split("\n") if p.strip()]
        except Exception as e:
            self.logger.error(f"提取主席互动方式时出错: {str(e)}")
            return ["未能分析主席互动"]


def main():
    try:
        # 配置参数
        # api_key = os.environ.get("OPENAI_API_KEY")
        # base_url = os.environ.get("OPENAI_API_BASE")
        # csv_path = "speeches_2019_2024.csv"
        api_key = "sk-89MCCzur02bckkA4YBCFejU7KV7FNjzcGWkyT94kBftuD9oX"  # 直接在这里填入API密钥
        base_url = "https://api.tao-shen.com/v1"  # API基础URL
        csv_path = "speeches_2019_2024.csv"

        # 初始化分析器
        analyzer = LegislatorAnalyzer(
            csv_path=csv_path, api_key=api_key, base_url=base_url
        )

        # 选择要分析的议员
        member_name = "陳永光"

        print(f"\n=== 开始分析议员: {member_name} ===")

        # 生成议员智能体
        agent = analyzer.generate_speech_agent(member_name)

        # 创建分析结果字典
        analysis_results = {
            "basic_info": {
                "name": agent.profile["basic_info"]["name"],
                "active_period": {
                    "start": str(
                        agent.profile["basic_info"]["active_period"]["start"]
                    ),  # 转换为字符串
                    "end": str(
                        agent.profile["basic_info"]["active_period"]["end"]
                    ),  # 转换为字符串
                },
                "total_speeches": agent.profile["basic_info"]["total_speeches"],
                "speech_types": agent.profile["basic_info"]["speech_types"],
            },
            "political_stance": {
                "general_stance": agent.profile["political_stance"]["general_stance"],
                "core_values": agent.profile["political_stance"]["core_values"],
                "issue_positions": agent.profile["political_stance"]["issue_positions"],
                "consistency": agent.profile["political_stance"]["consistency"],
            },
            "expertise_areas": {
                "primary_areas": agent.profile["expertise_areas"]["primary_areas"],
                "knowledge_depth": agent.profile["expertise_areas"]["knowledge_depth"],
                "cross_domain": agent.profile["expertise_areas"]["cross_domain"],
            },
            "speech_patterns": {
                "qualitative_analysis": agent.profile["speech_patterns"][
                    "qualitative_analysis"
                ],
                "quantitative_analysis": {
                    k: (float(v) if isinstance(v, np.float64) else v)  # 转换numpy类型
                    for k, v in agent.profile["speech_patterns"][
                        "quantitative_analysis"
                    ].items()
                },
            },
            "speech_type_distribution": {
                k: (float(v) if isinstance(v, np.float64) else v)  # 转换numpy类型
                for k, v in agent.profile["speech_type_distribution"].items()
            },
            "interaction_patterns": agent.profile["interaction_patterns"],
        }

        # 保存为JSON文件
        import json

        output_file = f"legislator_analysis_{member_name}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=4)

        print(f"\n=== 分析结果已保存至 {output_file} ===")

        # 创建发言上下文
        context = SpeechContext(
            meeting_type="立法会会议",
            date=datetime.now(),
            topic="交通运输政策",
            background="讨论新的交通基建发展计划",
            related_bills=["《铁路发展策略2025》"],
            current_stage="二读辩论",
            current_mood="热烈讨论",
            time_limit=5,
        )

        # 生成发言
        print("\n=== 生成模拟发言 ===")
        speech = agent.generate_speech(context)
        print("\n生成的发言内容:")
        print(speech)

    except Exception as e:
        print(f"运行时出错: {str(e)}")
        raise e

    #     print("\n=== 议员档案分析完成 ===")
    #     print(f"基本信息: {agent.profile['basic_info']}")
    #     print("\n政治立场:")
    #     print(agent._format_political_stance())
    #     print("\n专业领域:")
    #     print(agent._format_expertise_areas())
    #     print("\n发言风格:")
    #     print(agent._format_speech_style())
    #     print("\n发言类型分布:")
    #     print(agent.profile["speech_type_distribution"])

    #     # 创建发言上下文
    #     context = SpeechContext(
    #         meeting_type="立法会会议",
    #         date=datetime.now(),
    #         topic="交通运输政策",
    #         background="讨论新的交通基建发展计划",
    #         related_bills=["《铁路发展策略2025》"],
    #         current_stage="二读辩论",
    #         current_mood="热烈讨论",
    #         time_limit=5,
    #     )

    #     # 生成发言
    #     print("\n=== 生成模拟发言 ===")
    #     speech = agent.generate_speech(context)
    #     print("\n生成的发言内容:")
    #     print(speech)

    # except Exception as e:
    #     print(f"运行时出错: {str(e)}")
    #     raise e


if __name__ == "__main__":
    main()
