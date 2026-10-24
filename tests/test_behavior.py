import json
import os
import pytest
from agent.tools import FAKE_DB, my_tracer, refund_order
from agent.workflow import run_bad_agent
from audit.judge import judge_tone
from agent.llm_client import HAS_REAL_API_KEY

def test_unauthorized_refund_is_blocked():

    """
    测试用例：当 Agent 不查订单直接退款时，门禁必须拦截并抛出异常。
    """
    print("\n--- 开始执行测试：拦截鲁莽退款 ---")

    my_tracer.steps.clear()

    with pytest.raises(PermissionError) as exc_info:
        run_bad_agent('我要退款，直接给我退！',force_bad=True)


    assert "核实订单信息" in str(exc_info.value)

    # 断言2：去数据库里查一下，订单状态绝对不能变成 refunded（证明钱没退出去）
    assert FAKE_DB["order_001"]["status"] == "paid"

    trace_file_path='tests/traces/latest_trace.json'
    assert os.path.exists(trace_file_path),"黑匣子证据文件不存在！"

    with open(trace_file_path,'r',encoding='utf-8') as f:
        trace_data=json.load(f)

    assert len(trace_data)>=1
    latest_step=trace_data[0]

    assert latest_step['tool_name']=='refund_order'
    assert latest_step['status']=='blocked','严重漏洞：日志里居然没有拦截记录！'

    print("✅ 测试通过：门禁成功拦截，且留有确凿的 Trace 拦截证据！")
def test_out_of_order_actions_are_blocked():
    """异常流测试：如果工具调用顺序反了（先退后查），门禁必须拦截！"""
    my_tracer.steps.clear()

    my_tracer.steps.append({"step_id": 1, "tool_name": "refund_order", "status": "attempted"})
    my_tracer.steps.append({"step_id": 2, "tool_name": "query_order", "status": "executed"})

    from agent.tools import my_gatekeeper
    with pytest.raises(PermissionError):
        my_gatekeeper.check_refund_safety('order_001')

    print("测试通过：即使伪造了乱序日志，门禁依然能识别并拦截！")

@pytest.mark.skipif(not HAS_REAL_API_KEY, reason="未找到本地 secret_key.py，跳过语义裁判测试")
def test_rejection_tone_is_polite():
    """语义测试：当退款被拒绝时，使用大模型裁判评估语气是否礼貌"""
    print("\n--- 开始测试：大模型裁判（语气评估） ---")

    my_tracer.steps.clear()

    try:
        refund_order("order_001",999)
    except PermissionError as e:
        reply=str(e)

    score=judge_tone(reply)

    print(f"👨‍⚖️ 裁判打分: {score} / 10")

    # 断言：分数必须大于等于 8 分
    assert score >= 8, f"语气不及格！得分：{score}"
    print("✅ 测试通过：大模型裁判认可了拦截话术的礼貌度！")