from audit.gatekeeper import Gatekeeper
from audit.tracer import Tracer

my_tracer = Tracer()
my_gatekeeper = Gatekeeper(my_tracer)

# 假数据库
FAKE_DB = {
    "order_001": {"user_id": "u_123", "amount": 100, "status": "paid"}
}


def query_order(order_id):
    # (假设黑匣子已经写好了，这里记录一下)
    my_tracer.log(tool_name="query_order", args={"order_id": order_id})
    print(f"🔍 [工具调用] 查询订单: {order_id}")
    return FAKE_DB.get(order_id)


def refund_order(order_id, amount):

    my_tracer.log(tool_name="refund_order",args={"order_id": order_id, "amount": amount},status="attempted")

    try:
        my_gatekeeper.check_refund_safety(order_id)
    except PermissionError as e:
        my_tracer.steps[-1]['status']='blocked'
        raise e

    my_tracer.steps[-1]['status']='executed'

    print(f"💸 [高危操作] 执行退款: {order_id}, 金额: {amount} 元")

    # 判断订单是否存在 (相当于 Java 的 map.containsKey)
    if order_id in FAKE_DB:
        # 修改状态 (相当于 map.get(order_id).put("status", "refunded"))
        FAKE_DB[order_id]["status"] = "refunded"

    return "退款成功"
