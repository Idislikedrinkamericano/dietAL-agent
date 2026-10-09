# 🍱 DietAL Agent

这是一个用 LangGraph 做的简单饮食记录 Agent。

你只需要输入一句人话，比如：

```text
午饭吃了两碗米饭和200g鸡胸肉
```

程序会依次做几件事：

1. 看懂你吃了什么；
2. 估算热量、蛋白质、碳水和脂肪；
3. 把这顿饭记进今天的记录；
4. 算出今天累计吃了多少；
5. 给你一句简单反馈。

[English README](README.md)

---

## 这个项目到底是干什么的？

这是一个用来学习 AI Agent / LangGraph 的小项目。

现在它的流程非常简单：

```text
你输入一句话
    ↓
解析你吃了什么
    ↓
查询食物营养
    ↓
记录到今天
    ↓
给你反馈
```

如果你配置了 OpenAI API Key：

> 第一步“解析你吃了什么”会优先用 LLM。

如果你没有 API Key：

> 也能正常运行，只是会使用比较简单的关键词 + 正则解析。

热量和营养数据不会让 LLM 随便猜，而是由本地的食物数据库来计算。

---

# 怎么打开和使用？

下面按最普通的 Mac 用户来写。

## 第 1 步：打开 Terminal

在 Mac 上：

1. 按 `Command + Space`
2. 搜索 `Terminal`
3. 打开 Terminal

你之后所有命令都输入在这里。

---

## 第 2 步：把项目下载到电脑

在 Terminal 输入：

```bash
git clone https://github.com/Idislikedrinkamericano/dietAL-agent.git
```

这句话的意思是：

> 把 GitHub 上的 DietAL Agent 下载到你的电脑。

下载好以后，进入项目文件夹：

```bash
cd dietAL-agent
```

这句话的意思是：

> 让 Terminal 进入这个项目。

---

## 第 3 步：创建 Python 虚拟环境

输入：

```bash
python3 -m venv .venv
```

然后输入：

```bash
source .venv/bin/activate
```

如果成功，你的 Terminal 前面一般会出现：

```text
(.venv)
```

可以简单理解成：

> 现在我们给这个项目单独准备了一个 Python 环境，不会和电脑其他项目混在一起。

---

## 第 4 步：安装项目需要的东西

输入：

```bash
python -m pip install -r requirements.txt
```

这句话不用想复杂。

它的意思就是：

> 按照 `requirements.txt` 这个清单，把项目需要的 Python 包一次性装好。

例如这里会安装 LangGraph、OpenAI SDK 等。

通常第一次运行项目时装一次就够了。

---

## 第 5 步：真正启动 DietAL Agent

输入：

```bash
python demo.py
```

这句话的意思就是：

> 运行 `demo.py`，把 DietAL Agent 打开。

如果正常，你会看到类似：

```text
🍱 饭搭子 Diet Agent 启动！
>
```

看到 `>` 以后，就可以直接输入你吃了什么。

例如：

```text
> 午饭吃了两碗米饭和200g鸡胸肉
```

然后按 Enter。

---

# 程序打开以后能输入什么？

正常饮食记录：

```text
早餐吃了两个鸡蛋和一杯牛奶
```

或者：

```text
晚饭吃了一碗米饭和200g牛肉
```

---

## 查看今天一共吃了多少

输入：

```text
/today
```

它会告诉你今天累计的：

- 热量
- 蛋白质
- 碳水
- 脂肪

---

## 查看目前的饮食目标

输入：

```text
/goals
```

---

## 退出程序

输入：

```text
quit
```

---

# 没有 OpenAI API Key 可以用吗？

**可以。**

你完全不配置 API Key，也可以运行：

```bash
python demo.py
```

这时程序使用本地的简单解析方式。

例如：

```text
两碗米饭
200g鸡胸肉
两个鸡蛋
```

这类比较明确的表达通常可以识别。

---

# API Key 是干什么的？

如果配置 OpenAI API Key，程序就可以用 LLM 来理解你说的话。

例如这种表达：

```text
中午大概吃了半碗饭，一个鸡蛋，还有差不多200g鸡胸肉
```

相比简单关键词匹配，LLM 更擅长把这种自然语言整理成结构化数据。

配置方法：

```bash
export OPENAI_API_KEY="你的API Key"
python demo.py
```

注意：

**不要把真正的 API Key 写进 GitHub，也不要 commit 到代码里。**

目前默认模型是：

```text
gpt-4.1-mini
```

如果 LLM 调用失败，程序会自动退回本地解析器，不会直接崩掉。

---

# 这个 Agent 内部到底发生了什么？

现在一共四步。

### 1. parse_meal

负责：

> 看懂你刚才说自己吃了什么。

例如：

```text
两碗米饭 + 200g鸡胸肉
```

会整理成类似：

```text
米饭：2份
鸡胸肉：2份100g
```

### 2. estimate_nutrition

负责：

> 去本地食物数据库查营养，然后做计算。

这里不是让 LLM 随便猜热量。

### 3. update_log

负责：

> 把这一顿加到今天的饮食记录里。

记录会保存在：

```text
data/daily_log.json
```

### 4. feedback

负责：

> 看看你今天累计吃了多少，再给一句简单建议。

所以 LangGraph 在这个项目里的作用，可以先简单理解成：

> 规定这四步按照什么顺序执行。

---

# 项目文件分别是干什么的？

```text
dietAL-agent/
├── demo.py
├── requirements.txt
├── diet_agent/
│   ├── graph.py
│   ├── llm_parser.py
│   ├── nutrition_db.py
│   ├── state.py
│   └── store.py
```

简单理解：

- `demo.py`：真正打开程序的入口
- `graph.py`：规定 Agent 一步一步怎么运行
- `llm_parser.py`：让 LLM 帮忙理解你吃了什么
- `nutrition_db.py`：食物营养数据库 + 营养计算
- `state.py`：保存 Agent 每一步之间传递的数据
- `store.py`：把今天吃的东西保存下来
- `requirements.txt`：这个项目需要安装哪些 Python 包

---

# 现在这个项目还缺什么？

它现在还是一个学习型的小项目，不是完整的饮食 App。

目前主要限制是：

- 食物数据库还比较小；
- 不是所有食物都认识；
- 每日目标还不能自然语言修改；
- 还没有真正的对话记忆；
- 还没有拍照识别。

下一步会继续加入：

1. Nutrition Tool
2. 自定义热量 / 蛋白目标
3. Memory
4. 更自然的反馈
5. 食物图片识别
