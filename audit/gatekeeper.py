import yaml

class Gatekeeper:
    def __init__(self,tracer,config_path="config/rules.yaml"):
        self.tracer = tracer

        with open(config_path,"r",encoding="utf-8") as f:
            self.rules=yaml.safe_load(f)

    def check_refund_safety(self,order_id):
        print("🛡️ 保安开始检查退款前置条件...")

        executed_tools=[step['tool_name']for step in self.tracer.steps]

        refund_rules=self.rules.get("refund_rules",[])

        for rule  in refund_rules:
            required_tools=rule.get("required_preceding_tools",[])
            error_msg=rule.get("error_message",'拦截！')

            for required in required_tools:
                if required not in executed_tools:
                    raise PermissionError(error_msg)

                if "refund_order" in executed_tools:
                    query_inder=executed_tools.index(required)
                    refund_inder=executed_tools.index("refund_order")

                    if query_inder>refund_inder:
                        raise PermissionError("🛑 顺序错误！必须先查订单，再退款！")
        print("✅ [门禁放行] 前置检查通过，允许退款。")