from __future__ import annotations

from typing import Tuple

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message, Plan

class QuestionConst:
    QUESTION_TRIGGER = "question"

    KNOW_WORDS = ["answer", "ans", "a"]
    DONT_KNOW_WORDS = ["skip","s"]
    END_WORDS = ["end"]
    EXIT_WORDS = ["exit"]

    QUESTION_INSTRUCTION = (
        f"If you know the answer of the question, say '... (your answer)' "
        f"If you don't know the answer, say '{DONT_KNOW_WORDS[0]} ... (your change advice)' "
        f"If you want to skip all the question, say '{END_WORDS[0]}' "
    )
    EXIT_INSTRUCTION = f"If you want to terminate the process, type: {EXIT_WORDS[0]}"


class AskQuestion(Action):
    async def run(
        self, context: list[Message] = [], questions = [str], trigger: str = QuestionConst.QUESTION_TRIGGER
    ) -> Tuple[str, bool]:
        if questions:
            logger.info("Current overall question:")
            print(questions)
            # 每个question后拼接一个换行符
            questions_str = "\n".join(questions)

            

        question_instruction = (
            QuestionConst.QUESTION_INSTRUCTION
            if trigger == QuestionConst.QUESTION_TRIGGER
            else QuestionConst.QUESTION_INSTRUCTION
        )
        question_number = len(questions)
        answered = False
        answer_all = ""
        prompt = (
            f"I have serveral questions.All of them are listed below:\n"
            f"{questions_str}\n"
        )
        print(prompt)

        for cur_question_number in range(question_number):
            prompt = (
                f"-------------\n"
                f"Current question is: {questions[cur_question_number]}.\n"
                f"{question_instruction}\n"
                f"{QuestionConst.EXIT_INSTRUCTION}\n"
                "Please type your answer below:\n"
            )
            rsp = input(prompt)
            if rsp.lower() in QuestionConst.END_WORDS:
                break
            if rsp.lower() in QuestionConst.EXIT_WORDS:
                exit()
            
            answered = True
            answer_all += f'Question {cur_question_number+1}: {questions[cur_question_number]}\n Answer: {rsp}\n'

        return answer_all, answered