# 🍱 DietAL Agent

这是一个用 LangGraph 做的简单饮食记录 Agent。

你输入一句“我吃了什么”，它会：

```text
你的输入
   ↓
解析食物
   ↓
查询营养
   ↓
记录到今天
   ↓
给出反馈
```

如果配置了 OpenAI API Key，第一步会优先用 LLM；没有 Key 也能运行，会自动使用本地解析器。

营养数值来自本地食物数据库，不是让 LLM 随便猜。

[English README](README.md)

## 怎么运行

Mac 上打开 Terminal，然后**整段复制粘贴下面这些命令**：

```bash
git clone https://github.com/Idislikedrinkamericano/dietAL-agent.git
cd dietAL-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py
```

简单理解：

- `git clone ...`：把项目下载到电脑
- `cd dietAL-agent`：进入项目文件夹
- `python3 -m venv .venv`：创建独立 Python 环境
- `source .venv/bin/activate`：进入这个环境
- `python -m pip install -r requirements.txt`：安装项目需要的包
- `python demo.py`：启动程序

启动后会看到：

```text
🍱 饭搭子 Diet Agent 启动！
>
```

然后直接输入，例如：

```text
> 午饭吃了两碗米饭和200g鸡胸肉
```

## 常用命令

```text
/today   查看今天累计营养
/goals   查看每日目标
/undo    撤销上一条记录
quit     退出
```

## 可选：开启 LLM 解析

如果你想让它更好地理解自然语言：

```bash
export OPENAI_API_KEY="你的API Key"
python demo.py
```

不要把真实 API Key 上传到 GitHub。

## 主要文件

- `demo.py`：启动程序
- `diet_agent/graph.py`：LangGraph 流程
- `diet_agent/llm_parser.py`：LLM 负责理解饮食描述
- `diet_agent/nutrition_db.py`：食物库 + 营养计算
- `diet_agent/store.py`：保存每天的记录
- `diet_agent/state.py`：Graph 每一步共享的数据

## 目前的限制

现在还是学习型项目：

- 食物数据库不大
- 餐厅品牌和具体菜单商品还不够准确
- 还没有完整的对话记忆

下一步准备加入 Nutrition Tool、自定义目标、Memory 和图片输入。
