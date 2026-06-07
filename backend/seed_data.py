"""
种子数据脚本 — 填充词库、语法知识库、跟读素材
运行方式: python backend/seed_data.py
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 动态路径
import sys, os

# 切换到 backend 目录，确保 .env 被正确加载
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app.core.config import settings
from app.core.database import Base
from app.models.user import StudyStage
from app.models.word import Word, WordBank
from app.models.grammar import GrammarTopic
from app.models.speak import AccentType, DifficultyLevel, SpeakMaterial, SpeakSentence

engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_word_banks():
    """创建词库和示例单词"""
    async with SessionLocal() as db:
        # 清空已有数据
        await db.execute(delete(Word))
        await db.execute(delete(WordBank))

        banks = [
            WordBank(
                id=str(uuid.uuid4()),
                name="小学英语核心词 300",
                stage=StudyStage.ELEMENTARY,
                description="覆盖小学三年级至六年级教材同步核心词汇",
            ),
            WordBank(
                id=str(uuid.uuid4()),
                name="初中英语中考词 800",
                stage=StudyStage.MIDDLE_SCHOOL,
                description="初中三年教材词汇 + 中考高频词",
            ),
            WordBank(
                id=str(uuid.uuid4()),
                name="高中英语高考词 1500",
                stage=StudyStage.HIGH_SCHOOL,
                description="高中必修 + 选修核心词汇，高考高频考点",
            ),
            WordBank(
                id=str(uuid.uuid4()),
                name="大学英语四级核心 1200",
                stage=StudyStage.COLLEGE,
                description="四级考试高频词汇精选，含真题例句",
            ),
            WordBank(
                id=str(uuid.uuid4()),
                name="雅思核心词汇 500",
                stage=StudyStage.OVERSEAS,
                description="雅思听说读写四科高频词",
            ),
        ]
        db.add_all(banks)
        await db.flush()

        words_data = {
            # 小学
            "小学英语核心词 300": [
                ("apple", "ˈæp.l̩", "苹果", "I eat an apple every day.", "我每天吃一个苹果。", "n.", 1),
                ("book", "bʊk", "书；书籍", "She is reading a book.", "她正在读一本书。", "n.", 1),
                ("cat", "kæt", "猫", "The cat is sleeping on the sofa.", "猫在沙发上睡觉。", "n.", 1),
                ("dog", "dɒɡ", "狗", "He walks his dog every morning.", "他每天早上遛狗。", "n.", 1),
                ("elephant", "ˈel.ɪ.fənt", "大象", "An elephant has a long trunk.", "大象有长长的鼻子。", "n.", 1),
                ("family", "ˈfæm.əl.i", "家庭；家人", "I love my family.", "我爱我的家人。", "n.", 1),
                ("good", "ɡʊd", "好的", "This is a good idea.", "这是个好主意。", "adj.", 1),
                ("happy", "ˈhæp.i", "快乐的；高兴的", "She looks very happy today.", "她今天看起来很高兴。", "adj.", 1),
                ("ice", "aɪs", "冰", "Would you like some ice in your drink?", "你的饮料里要加冰吗？", "n.", 1),
                ("jump", "dʒʌmp", "跳；跳跃", "The rabbit can jump very high.", "这只兔子能跳得很高。", "v.", 1),
            ],
            # 初中
            "初中英语中考词 800": [
                ("abandon", "əˈbæn.dən", "放弃；抛弃", "Never abandon your dreams.", "永远不要放弃你的梦想。", "v.", 2),
                ("benefit", "ˈben.ɪ.fɪt", "益处；好处", "Exercise has many benefits for health.", "锻炼对健康有很多好处。", "n.", 2),
                ("concentrate", "ˈkɒn.sən.treɪt", "集中；专注", "I can't concentrate with all this noise.", "这些噪音让我无法集中注意力。", "v.", 2),
                ("discover", "dɪˈskʌv.ər", "发现", "Scientists discovered a new planet.", "科学家发现了一颗新的行星。", "v.", 2),
                ("environment", "ɪnˈvaɪ.rən.mənt", "环境", "We should protect the environment.", "我们应该保护环境。", "n.", 2),
                ("frequently", "ˈfriː.kwənt.li", "频繁地；经常", "She frequently visits her grandparents.", "她经常去看望祖父母。", "adv.", 2),
                ("government", "ˈɡʌv.ən.mənt", "政府", "The government announced new policies.", "政府宣布了新政策。", "n.", 2),
                ("honest", "ˈɒn.ɪst", "诚实的", "An honest person never tells lies.", "诚实的人从不说谎。", "adj.", 2),
                ("immediately", "ɪˈmiː.di.ət.li", "立刻；马上", "Please call me immediately if there is an emergency.", "如果有紧急情况请立刻给我打电话。", "adv.", 2),
                ("journey", "ˈdʒɜː.ni", "旅行；旅程", "The journey took about three hours.", "这次旅程大约花了三个小时。", "n.", 2),
            ],
            # 高中
            "高中英语高考词 1500": [
                ("acknowledge", "əkˈnɒl.ɪdʒ", "承认；感谢", "He acknowledged his mistake publicly.", "他公开承认了自己的错误。", "v.", 3),
                ("bureaucracy", "bjʊˈrɒk.rə.si", "官僚机构；官僚作风", "The paperwork was delayed by bureaucracy.", "文书工作被官僚程序拖延了。", "n.", 3),
                ("controversial", "ˌkɒn.trəˈvɜː.ʃəl", "有争议的", "This is a highly controversial topic.", "这是一个高度有争议的话题。", "adj.", 3),
                ("deteriorate", "dɪˈtɪə.ri.ə.reɪt", "恶化；变坏", "His health began to deteriorate rapidly.", "他的健康状况开始迅速恶化。", "v.", 3),
                ("exaggerate", "ɪɡˈzædʒ.ə.reɪt", "夸张；夸大", "Don't exaggerate the difficulty of the task.", "不要夸大任务的难度。", "v.", 3),
                ("fundamental", "ˌfʌn.dəˈmen.təl", "基本的；根本的", "This is a fundamental principle of physics.", "这是物理学的基本原理。", "adj.", 3),
                ("guarantee", "ˌɡær.ənˈtiː", "保证；担保", "Hard work is no guarantee of success.", "努力并不能保证成功。", "v./n.", 3),
                ("hypothesis", "haɪˈpɒθ.ə.sɪs", "假说；假设", "The scientist tested her hypothesis with experiments.", "科学家通过实验验证了她的假说。", "n.", 3),
                ("inevitable", "ɪˈnev.ɪ.tə.bəl", "不可避免的", "Change is an inevitable part of life.", "变化是生活中不可避免的一部分。", "adj.", 3),
                ("justify", "ˈdʒʌs.tɪ.faɪ", "证明…有理；辩解", "How can you justify such behavior?", "你如何为这种行为辩解？", "v.", 3),
            ],
            # 四级
            "大学英语四级核心 1200": [
                ("access", "ˈæk.ses", "进入；通道；访问", "Students have free access to the library.", "学生可以免费进入图书馆。", "n./v.", 3),
                ("capable", "ˈkeɪ.pə.bəl", "有能力的", "She is capable of handling complex problems.", "她有能力处理复杂的问题。", "adj.", 3),
                ("demonstrate", "ˈdem.ən.streɪt", "展示；证明", "The experiment demonstrates the theory.", "这个实验证明了理论。", "v.", 3),
                ("efficient", "ɪˈfɪʃ.ənt", "高效的", "This new system is more efficient than the old one.", "这个新系统比旧系统效率更高。", "adj.", 3),
                ("flexible", "ˈflek.sə.bəl", "灵活的；可变通的", "We need a more flexible approach to this problem.", "我们需要更灵活的方法来解决这个问题。", "adj.", 3),
                ("generate", "ˈdʒen.ər.eɪt", "产生；生成", "The wind turbines generate electricity for the town.", "风力涡轮机为镇上发电。", "v.", 3),
                ("identify", "aɪˈden.tɪ.faɪ", "识别；确认", "Police are trying to identify the suspect.", "警方正在试图确认嫌疑人身份。", "v.", 3),
                ("maintain", "meɪnˈteɪn", "维持；保养", "It's important to maintain a healthy lifestyle.", "保持健康的生活方式很重要。", "v.", 3),
                ("negotiate", "nɪˈɡəʊ.ʃi.eɪt", "谈判；协商", "The two companies are negotiating a merger.", "两家公司正在谈判合并事宜。", "v.", 3),
                ("obtain", "əbˈteɪn", "获得；得到", "She obtained her degree from Harvard.", "她从哈佛大学获得了学位。", "v.", 3),
            ],
            # 雅思
            "雅思核心词汇 500": [
                ("alleviate", "əˈliː.vi.eɪt", "减轻；缓解", "This medicine can alleviate the pain.", "这种药可以缓解疼痛。", "v.", 4),
                ("bias", "ˈbaɪ.əs", "偏见；倾向", "The study was criticized for its selection bias.", "该研究因其选择偏见而受到批评。", "n.", 4),
                ("contemplate", "ˈkɒn.təm.pleɪt", "沉思；考虑", "She contemplated changing her career path.", "她考虑改变职业方向。", "v.", 4),
                ("dilemma", "daɪˈlem.ə", "困境；两难", "He faced a moral dilemma in his decision.", "他在决策中面临道德困境。", "n.", 4),
                ("elaborate", "iˈlæb.ər.ət", "详细的；精心制作的", "Please give us an elaborate explanation.", "请给我们一个详细的解释。", "adj.", 4),
                ("feasible", "ˈfiː.zə.bəl", "可行的", "Is this plan financially feasible?", "这个计划在经济上可行吗？", "adj.", 4),
                ("genuine", "ˈdʒen.ju.ɪn", "真正的；真诚的", "She showed genuine interest in the project.", "她对这个项目表现出了真正的兴趣。", "adj.", 4),
                ("hierarchy", "ˈhaɪə.rɑː.ki", "等级制度；层次", "The company has a strict hierarchy.", "这家公司有严格的等级制度。", "n.", 4),
                ("inevitable", "ɪˈnev.ɪ.tə.bəl", "不可避免的", "Some degree of risk is inevitable.", "某种程度的风险是不可避免的。", "adj.", 4),
                ("jeopardize", "ˈdʒep.ə.daɪz", "危及；危害", "Don't jeopardize your health for money.", "不要为了钱而危害你的健康。", "v.", 4),
            ],
        }

        for bank in banks:
            wlist = words_data.get(bank.name, [])
            for (word_text, phonetic, definition, example, trans, pos, diff) in wlist:
                db.add(
                    Word(
                        id=str(uuid.uuid4()),
                        word_bank_id=bank.id,
                        word=word_text,
                        phonetic=phonetic,
                        definition=definition,
                        example_sentence=example,
                        example_translation=trans,
                        part_of_speech=pos,
                        difficulty=diff,
                    )
                )
            bank.word_count = len(wlist)

        await db.commit()
        print(f"✅ 词库: 5 个词库, 共 {sum(len(v) for v in words_data.values())} 个单词")


async def seed_grammar_topics():
    """创建语法知识库（树状结构）"""
    async with SessionLocal() as db:
        await db.execute(delete(GrammarTopic))

        # 根节点
        topics = [
            ("词性 Parts of Speech", None, 1),
            ("句子成分 Sentence Components", None, 2),
            ("时态与语态 Tense & Voice", None, 3),
            ("从句 Clauses", None, 4),
            ("特殊句式 Special Sentence Patterns", None, 5),
        ]

        topic_map = {}
        for title, parent_id, order in topics:
            t = GrammarTopic(
                id=str(uuid.uuid4()),
                title=title,
                content=f"# {title}\n\n本模块涵盖{title}的核心知识点。",
                sort_order=order,
            )
            db.add(t)
            topic_map[title] = t

        await db.flush()

        # 子节点
        children = [
            # 词性子节点
            ("名词 Noun", topic_map["词性 Parts of Speech"].id, "名词是表示人、事物、地点或抽象概念的词。\n\n- 可数名词: book, apple, cat\n- 不可数名词: water, air, information\n- 专有名词: China, Shakespeare"),
            ("动词 Verb", topic_map["词性 Parts of Speech"].id, "动词表示动作或状态。\n\n- 及物动词: eat, read, build\n- 不及物动词: sleep, arrive, go\n- 系动词: be, become, seem"),
            ("形容词 Adjective", topic_map["词性 Parts of Speech"].id, "形容词修饰名词或代词，表示性质或特征。\n\n- 比较级: bigger, more beautiful\n- 最高级: biggest, most beautiful"),
            ("副词 Adverb", topic_map["词性 Parts of Speech"].id, "副词修饰动词、形容词或其他副词。\n\n- 方式副词: quickly, carefully\n- 频率副词: always, often, never\n- 程度副词: very, quite, extremely"),
            # 句子成分
            ("主语 Subject", topic_map["句子成分 Sentence Components"].id, "主语是句子的主体，通常由名词、代词或名词性成分担任。\n\n例: **The cat** is sleeping.\n例: **She** loves music."),
            ("谓语 Predicate", topic_map["句子成分 Sentence Components"].id, "谓语说明主语的动作或状态，由动词或动词短语构成。\n\n例: She **is reading** a book.\n例: They **have finished** the work."),
            ("宾语 Object", topic_map["句子成分 Sentence Components"].id, "宾语是动作的承受者。\n\n- 直接宾语: I bought **a car**.\n- 间接宾语: She gave **me** a gift."),
            # 时态
            ("一般现在时 Simple Present", topic_map["时态与语态 Tense & Voice"].id, "表示经常发生的动作或状态。\n\n结构: 主语 + 动词原形 (三单 +s/es)\n例: He **reads** books every day.\n例: Water **boils** at 100°C."),
            ("一般过去时 Simple Past", topic_map["时态与语态 Tense & Voice"].id, "表示过去发生的动作。\n\n结构: 主语 + 动词过去式\n例: She **went** to Beijing last year.\n例: I **saw** a movie yesterday."),
            ("现在完成时 Present Perfect", topic_map["时态与语态 Tense & Voice"].id, "表示过去动作对现在的影响或持续。\n\n结构: have/has + 过去分词\n例: I **have finished** my homework.\n例: She **has lived** here for 10 years."),
            # 从句
            ("定语从句 Relative Clause", topic_map["从句 Clauses"].id, "修饰名词或代词的从句。\n\n- 关系代词: who, which, that\n- 关系副词: when, where, why\n例: The book **that I borrowed** is excellent."),
            ("状语从句 Adverbial Clause", topic_map["从句 Clauses"].id, "修饰动词、形容词或整个句子的从句。\n\n- 时间: when, while, after\n- 原因: because, since\n- 条件: if, unless\n例: I'll call you **when I arrive**."),
            ("名词性从句 Noun Clause", topic_map["从句 Clauses"].id, "在句中充当名词角色的从句。\n\n- 主语从句: **What he said** surprised me.\n- 宾语从句: I don't know **where she is**."),
            # 特殊句式
            ("倒装句 Inversion", topic_map["特殊句式 Special Sentence Patterns"].id, "将谓语或助动词提到主语之前。\n\n- 完全倒装: Here **comes** the bus.\n- 部分倒装: **Never have I** seen such beauty.\n例: Not until then **did I realize** my mistake."),
            ("强调句 Emphasis", topic_map["特殊句式 Special Sentence Patterns"].id, "使用 It is/was ... that/who ... 结构强调。\n\n例: **It was** John **who** broke the window.\n例: **It is** at midnight **that** the train arrives."),
        ]

        for title, parent_id, content in children:
            db.add(
                GrammarTopic(
                    id=str(uuid.uuid4()),
                    parent_id=parent_id,
                    title=title,
                    content=content,
                    sort_order=0,
                )
            )

        await db.commit()
        print(f"✅ 语法知识库: 5 个根节点 + {len(children)} 个子节点")


async def seed_speak_materials():
    """创建跟读素材"""
    async with SessionLocal() as db:
        await db.execute(delete(SpeakSentence))
        await db.execute(delete(SpeakMaterial))

        materials = [
            SpeakMaterial(
                id=str(uuid.uuid4()),
                title="日常问候 — Everyday Greetings",
                description="基础日常问候对话，适合初学者",
                category="教材对话",
                accent=AccentType.AMERICAN,
                difficulty=DifficultyLevel.BEGINNER,
                audio_url="https://example.com/audio/greetings.mp3",
                cover_url=None,
            ),
            SpeakMaterial(
                id=str(uuid.uuid4()),
                title="Steve Jobs — Stanford Commencement Speech",
                description="乔布斯 2005 年斯坦福大学毕业演讲经典片段",
                category="名人演讲",
                accent=AccentType.AMERICAN,
                difficulty=DifficultyLevel.INTERMEDIATE,
                audio_url="https://example.com/audio/steve_jobs.mp3",
                cover_url=None,
            ),
            SpeakMaterial(
                id=str(uuid.uuid4()),
                title="The Lion King — Remember Who You Are",
                description="《狮子王》经典台词片段",
                category="影视台词",
                accent=AccentType.AMERICAN,
                difficulty=DifficultyLevel.ELEMENTARY,
                audio_url="https://example.com/audio/lion_king.mp3",
                cover_url=None,
            ),
        ]

        db.add_all(materials)
        await db.flush()

        sentences_data = {
            "日常问候 — Everyday Greetings": [
                ("Hello, how are you today?", "你好，今天过得怎么样？", 1),
                ("I'm doing great, thank you!", "我很好，谢谢你！", 2),
                ("What a beautiful day it is!", "今天天气真好！", 3),
                ("Shall we go for a walk in the park?", "我们去公园散步好吗？", 4),
                ("That sounds like a wonderful idea.", "这听起来是个好主意。", 5),
            ],
            "Steve Jobs — Stanford Commencement Speech": [
                ("Your time is limited, so don't waste it living someone else's life.", "你的时间有限，所以不要浪费在过别人的生活上。", 1),
                ("Don't let the noise of others' opinions drown out your own inner voice.", "不要让别人的意见淹没了你自己内心的声音。", 2),
                ("Stay hungry, stay foolish.", "求知若渴，虚心若愚。", 3),
                ("I have looked in the mirror every morning and asked myself: If today were the last day of my life, would I want to do what I am about to do today?", "每天早晨我对着镜子问自己：如果今天是我生命中的最后一天，我还会想做今天要做的事吗？", 4),
            ],
            "The Lion King — Remember Who You Are": [
                ("Look inside yourself. You are more than what you have become.", "看看你自己的内心。你比现在的自己更加伟大。", 1),
                ("Remember who you are.", "记住你是谁。", 2),
                ("You must take your place in the Circle of Life.", "你必须在生命之环中找到自己的位置。", 3),
                ("The past can hurt, but the way I see it, you can either run from it or learn from it.", "过去可能会伤痛，但在我看来，你要么逃避它，要么从中学习。", 4),
            ],
        }

        for mat in materials:
            sdata = sentences_data.get(mat.title, [])
            for text, translation, order in sdata:
                db.add(
                    SpeakSentence(
                        id=str(uuid.uuid4()),
                        material_id=mat.id,
                        text=text,
                        translation=translation,
                        sort_order=order,
                    )
                )

        await db.commit()
        print(f"✅ 跟读素材: 3 篇素材, 共 {sum(len(v) for v in sentences_data.values())} 个句子")


async def seed_all():
    print("🌱 开始填充种子数据...\n")
    await seed_word_banks()
    await seed_grammar_topics()
    await seed_speak_materials()
    print("\n🎉 种子数据填充完成！")


if __name__ == "__main__":
    asyncio.run(seed_all())
