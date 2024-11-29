# -*- encoding: utf-8 -*-
"""
@Date    :   2024/11/29 19:24:03
@Author  :   yueyingwu
@File    :   write_question.py
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Tuple

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message, Plan, Task
from metagpt.strategy.task_type import TaskType
from metagpt.utils.common import CodeParser


class WriteQuestion(Action):
    PROMPT_TEMPLATE: str = """
    # Context:
    {context}
    # Task:
    Based on the given context, your goal is to ask clarifying and necessary questions to gather all missing information required to complete the programming task. 
    You can ask up to {max_question} questions.
    These questions should address potential gaps such as: Specific file paths, Relevant column names in datasets, User expectations for performance or functionality and so on.
    If you don't have any questions, you should output an empty list.
    Output a list of strings, each string represents a question you want to ask.
    ```json
    [
        "the question you want to ask",
        ...
    ]
    ```
    """

    async def run(self, context: list[Message], max_question: int = 2) -> str:
        task_type_desc = "\n".join([f"- **{tt.type_name}**: {tt.value.desc}" for tt in TaskType])
        prompt = self.PROMPT_TEMPLATE.format(
            context="\n".join([str(ct) for ct in context]), max_question=max_question
        )
        rsp = await self._aask(prompt)
        rsp = CodeParser.parse_code(block=None, text=rsp)
        return rsp


def get_question_from_rsp(rsp: str):
    rsp = json.loads(rsp)
    questions = rsp
    return questions


def precheck_get_question_from_rsp(rsp: str) -> Tuple[bool, str]:
    try:
        questions = get_question_from_rsp(rsp)
        return True, "", questions
    except Exception as e:
        return False, e, []
