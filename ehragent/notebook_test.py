import asyncio
from metagpt.actions.di.execute_nb_code import ExecuteNbCode

# 创建执行器实例
execute_code = ExecuteNbCode()

# 要执行的代码
code = '''

! pwd
! which python
print("Hello, World!")
'''

code2 = '''

print("code2 Hello, World!")

'''
# 异步执行代码
async def main():
    output, success = await execute_code.run(code=code, language="python")
    print(f"执行结果:\n{output}\n是否成功: {success}")

# 运行异步函数
asyncio.run(main())




