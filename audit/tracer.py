import json
import datetime
import time

class Tracer:
    def __init__(self):
        self.steps=[]
        self.statr_time=time.perf_counter()

    def log(self, tool_name, args,status='executed',token_usage=0):
        latency_ms=round((time.perf_counter()-self.statr_time)*1000,2)

        step={
            'step_id':len(self.steps)+1,
            'time':datetime.datetime.now().strftime('%H:%M:%S'),
            'tool_name':tool_name,
            'args':args,
            'status':status,
            'latency_ms':latency_ms,
            'token_usage':token_usage,
        }

        self.steps.append(step)

        print(f"📝 [黑匣子记录] 第{step['step_id']}步：调用了{tool_name}")

    def save_to_file(self, filepath):

        with open(filepath, 'w',encoding='utf-8') as f:
            json.dump(self.steps, f, ensure_ascii=False, indent=2)
        print(f"💾 [黑匣子存证] Trace 已保存至 {filepath}")