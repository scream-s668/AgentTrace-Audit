from agent.llm_client import ask_llm

def judge_tone(ai_reply:str)->int:
    """使用大模型给 AI 的回复语气打分（0-10分）"""
    prompt = f"""
        你是一个严格的客服质检员。请给下面这句客服回复打分（0-10分）。
        评分标准：必须包含拒绝理由，且语气礼貌。
        客服回复："{ai_reply}"

        请只输出一个数字（0-10），不要任何解释。
        """
    score_str=ask_llm(prompt)
    try:
        return int(score_str.strip())
    except:
        return 0