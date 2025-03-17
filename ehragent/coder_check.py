
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.actions.di.execute_nb_code import ExecuteNbCode

# 创建两个实例并检查 ID
di1 = DataInterpreter(execute_code=ExecuteNbCode())
print(f"Instance 1 ID: {id(di1.execute_code)}")
print(f"Instance 1 execute_code ID: {id(di1.execute_code)}")

di2 = DataInterpreter(execute_code=ExecuteNbCode())
print(f"Instance 2 ID: {id(di2.execute_code)}")
print(f"Instance 2 execute_code ID: {id(di2.execute_code)}")

# 如果输出不同 ID，则每次都是新实例
# 如果相同，说明存在共享问题
