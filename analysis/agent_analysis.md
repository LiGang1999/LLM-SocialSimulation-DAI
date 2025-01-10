

# 立法会议员发言分析与生成系统

## 项目概述
这是一个用于分析立法会议员发言模式并生成模拟发言的智能系统。该系统使用自然语言处理和机器学习技术，通过分析历史发言记录，构建议员个性化的发言模型。

## 主要功能

### 1. 发言文本分析
- 中文分词和文本清理
- 关键词提取
- 立法术语识别
- 发言类型分类
- 情感倾向分析

### 2. 议员画像构建
系统会分析并构建包含以下方面的议员画像：
- 基本信息统计
- 政治立场分析
- 专业领域识别
- 发言风格特征
- 互动模式分析

### 3. 智能发言生成
基于以下上下文信息生成符合议员风格的模拟发言：
- 会议类型
- 议题背景
- 相关法案
- 当前阶段
- 会议氛围
- 时间限制

## 完整运行流程

```python
def run_complete_analysis_and_generation(
    csv_path: str,
    member_name: str,
    context: SpeechContext
) -> Dict:
    """运行完整的分析和生成流程"""
    try:
        # 1. 初始化
        analyzer, speeches_df = initialize_analysis_session(csv_path, member_name)
        
        # 2. 基础分析
        basic_stats = perform_basic_analysis(analyzer, speeches_df, member_name)
        
        # 3. 语义分析
        processed_speeches = [str(s) for s in speeches_df['Speeches']]
        semantic_features = perform_semantic_analysis(analyzer, processed_speeches)
        
        # 4. 上下文分析
        context_features = analyze_context(analyzer, speeches_df)
        
        # 5. 生成议员档案
        profile = analyzer.analyze_legislator(member_name)
        
        # 6. 生成新发言
        speech, quality = generate_speech(analyzer, context, profile)
        
        # 7. 整合结果
        results = {
            "basic_stats": basic_stats,
            "semantic_features": semantic_features,
            "context_features": context_features,
            "profile": profile,
            "generated_speech": {
                "content": speech,
                "quality_scores": quality.__dict__
            }
        }
        
        return results
        
    except Exception as e:
        logging.error(f"完整分析流程失败: {str(e)}")
        raise
```

## 核心组件

### 1. 文本处理器 (SimpleTokenizer)

```python
class SimpleTokenizer:
    ...
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
```

负责文本清理、分词、标点符号处理等基础文本处理任务。

### 2. 发言上下文管理 (SpeechContext)

```python
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
```

管理发言生成所需的各种上下文信息。

### 3. 发言质量评估 (SpeechQuality)

```python
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
```

评估发言的相关性、连贯性、说服力和专业性。

## 发言分析和生成的完整过程：

### 1. 数据输入和初始化

```python
def initialize_analysis_session(csv_path: str, member_name: str):
    """初始化分析会话"""
    try:
        # 初始化分析器
        analyzer = LegislatorAnalyzer(
            csv_path=csv_path,
            api_key="your-api-key",
            base_url="your-base-url"
        )
        
        # 加载议员数据
        speeches_df = analyzer.extract_member_speeches(member_name)
        if speeches_df.empty:
            raise ValueError(f"未找到议员 {member_name} 的发言记录")
            
        return analyzer, speeches_df
        
    except Exception as e:
        logging.error(f"初始化失败: {str(e)}")
        raise
```

### 2. 基础分析流程

```python
def perform_basic_analysis(analyzer: LegislatorAnalyzer, 
                         speeches_df: pd.DataFrame, 
                         member_name: str) -> Dict:
    """执行基础分析"""
    try:
        # 1. 文本预处理
        processed_speeches = []
        for _, row in speeches_df.iterrows():
            speech_text = str(row['Speeches'])
            processed_text = analyzer.tokenizer._clean_text(speech_text)
            processed_speeches.append(processed_text)
            
        # 2. 发言分类
        speech_types = [
            analyzer.speech_classifier.classify(speech)
            for speech in processed_speeches
        ]
        
        # 3. 基础统计
        basic_stats = {
            "total_speeches": len(processed_speeches),
            "speech_type_distribution": Counter(speech_types),
            "avg_speech_length": np.mean([len(s) for s in processed_speeches]),
            "time_span": {
                "start": speeches_df['MeetingDate'].min(),
                "end": speeches_df['MeetingDate'].max()
            }
        }
        
        return basic_stats
        
    except Exception as e:
        logging.error(f"基础分析失败: {str(e)}")
        raise
```

### 3. 深度语义分析

```python
def perform_semantic_analysis(analyzer: LegislatorAnalyzer, 
                            processed_speeches: List[str]) -> Dict:
    """执行深度语义分析"""
    try:
        semantic_features = {
            "topic_analysis": [],
            "stance_analysis": [],
            "argument_patterns": [],
            "professional_terms": set()
        }
        
        for speech in processed_speeches:
            # 1. 主题分析
            topics = analyzer.tokenizer.extract_keywords(speech, top_n=5)
            semantic_features["topic_analysis"].append(topics)
            
            # 2. 立场分析
            stance = analyzer._analyze_stance_distribution([speech])
            semantic_features["stance_analysis"].append(stance)
            
            # 3. 论证模式分析
            arguments = analyzer._extract_argument_patterns(speech)
            semantic_features["argument_patterns"].append(arguments)
            
            # 4. 专业术语识别
            terms = analyzer.tokenizer.find_legislative_terms(speech)
            semantic_features["professional_terms"].update(terms)
            
        return semantic_features
        
    except Exception as e:
        logging.error(f"语义分析失败: {str(e)}")
        raise
```

### 4. 上下文分析

```python
def analyze_context(analyzer: LegislatorAnalyzer, 
                   speeches_df: pd.DataFrame) -> Dict:
    """执行上下文分析"""
    try:
        context_features = {
            "dialogue_chains": [],
            "reference_patterns": [],
            "topic_evolution": [],
            "interaction_patterns": []
        }
        
        # 按时间排序
        sorted_speeches = speeches_df.sort_values('MeetingDate')
        
        # 创建滑动窗口
        window_size = 5
        for i in range(len(sorted_speeches) - window_size + 1):
            window = sorted_speeches.iloc[i:i+window_size]
            
            # 1. 分析对话链
            dialogue_chain = analyzer._analyze_dialogue_chain(window)
            context_features["dialogue_chains"].append(dialogue_chain)
            
            # 2. 分析引用模式
            references = analyzer._analyze_speech_references(
                window.iloc[-1]['Speeches'],
                window.iloc[:-1].to_dict('records')
            )
            context_features["reference_patterns"].append(references)
            
            # 3. 追踪主题演变
            topic_evolution = analyzer._track_topic_evolution(
                window['Speeches'].tolist()
            )
            context_features["topic_evolution"].append(topic_evolution)
            
            # 4. 分析互动模式
            interactions = analyzer._analyze_interactions(window)
            context_features["interaction_patterns"].append(interactions)
            
        return context_features
        
    except Exception as e:
        logging.error(f"上下文分析失败: {str(e)}")
        raise
```

### 5. 质量评估

```python
def evaluate_speech_quality(analyzer: LegislatorAnalyzer, 
                          speech: str, 
                          context: SpeechContext) -> SpeechQuality:
    """评估发言质量"""
    try:
        # 1. 相关性评估
        relevance = analyzer.speech_quality_evaluator._evaluate_relevance(
            speech, context
        )
        
        # 2. 连贯性评估
        coherence = analyzer.speech_quality_evaluator._evaluate_coherence(
            speech
        )
        
        # 3. 说服力评估
        persuasiveness = analyzer.speech_quality_evaluator._evaluate_persuasiveness(
            speech
        )
        
        # 4. 专业性评估
        professionalism = analyzer.speech_quality_evaluator._evaluate_professionalism(
            speech
        )
        
        return SpeechQuality(
            relevance=relevance,
            coherence=coherence,
            persuasiveness=persuasiveness,
            professionalism=professionalism
        )
        
    except Exception as e:
        logging.error(f"质量评估失败: {str(e)}")
        raise
```

### 6. 发言生成

```python
def generate_speech(analyzer: LegislatorAnalyzer, 
                   context: SpeechContext, 
                   profile: Dict) -> str:
    """生成新的发言"""
    try:
        # 1. 创建议员智能体
        agent = analyzer.generate_speech_agent(profile['basic_info']['name'])
        
        # 2. 生成发言
        speech = agent.generate_speech(context)
        
        # 3. 质量评估
        quality = evaluate_speech_quality(analyzer, speech, context)
        
        # 4. 如果质量不达标，重新生成
        max_attempts = 3
        attempt = 1
        while quality.get_overall_score() < 0.7 and attempt < max_attempts:
            speech = agent.generate_speech(context)
            quality = evaluate_speech_quality(analyzer, speech, context)
            attempt += 1
            
        return speech, quality
        
    except Exception as e:
        logging.error(f"发言生成失败: {str(e)}")
        raise
```

## 使用方法

### 1.配置环境变量：

```1004:1010:agent.py
        # 配置参数
        # api_key = os.environ.get("OPENAI_API_KEY")
        # base_url = os.environ.get("OPENAI_API_BASE")
        # csv_path = "speeches_2019_2024.csv"
        api_key = "xxxxxxxx"  # 直接在这里填入API密钥
        base_url = "xxxxxx"  # API基础URL
        csv_path = "speeches_2019_2024.csv"
```

### 2.运行分析：

```1078:1094:agent.py
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
```

### 3.使用示例

```python
def main():
    # 配置参数
    csv_path = "speeches_2019_2024.csv"
    member_name = "陳永光"
    
    # 创建上下文
    context = SpeechContext(
        meeting_type="立法会会议",
        date=datetime.now(),
        topic="交通运输政策",
        background="讨论新的交通基建发展计划",
        related_bills=["《铁路发展策略2025》"],
        current_stage="二读辩论",
        current_mood="热烈讨论",
        time_limit=5
    )
    
    try:
        # 运行完整流程
        results = run_complete_analysis_and_generation(
            csv_path, member_name, context
        )
        
        # 输出结果
        print("=== 分析结果 ===")
        print(f"基础统计: {results['basic_stats']}")
        print(f"生成的发言: {results['generated_speech']['content']}")
        print(f"发言质量: {results['generated_speech']['quality_scores']}")
        
        # 保存结果
        with open(f"analysis_results_{member_name}.json", "w", 
                 encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        logging.error(f"主程序运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

## 数据要求

系统需要包含以下字段的CSV格式发言记录：
- RundownID
- HansardID
- MeetingDate
- HansardType
- SectionID
- SectionName
- SpeakerID
- SpeakerName
- Speeches
- SeqNum
- HansardFileURL

## 注意事项
1. 需要配置有效的OpenAI API密钥
2. 确保输入数据的完整性和质量
3. 生成的发言仅供参考，需要人工审核
4. 系统性能受限于API调用限制和响应时间

## 技术栈
- Python 3.x
- pandas
- OpenAI API
- numpy
- dataclasses
- logging