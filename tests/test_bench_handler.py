import stakk
from stakk import bench_handler
import asyncio


##### Methods

def test_benchy_and_register():
    benchy = bench_handler.Benchy()
    stack_id = 'test'

    @stakk.register(stack_id)
    @benchy
    def func_add(x: int, y: int) -> int:
        """this is a test function"""
        return x + y

    @benchy
    @stakk.register(stack_id)
    def func_minus(x: int, y: int) -> int:
        """this is a test function"""
        return x - y
    
    @benchy
    @stakk.register(stack_id)
    def func_data(data: list) -> list:
        """this is a test function"""
        return data
    
    @stakk.register(stack_id)
    @benchy
    async def async_test():
        '''this is a test async function'''
        await asyncio.sleep(0.1)
        print("pass")

    # call the functions
    func_add(1, 2)
    func_minus(2, 1)
    func_data(data=[1,2,3])
    asyncio.get_event_loop().run_until_complete(async_test())

    # assert that reports were created\
    assert "func_add" in benchy.report
    assert "func_minus" in benchy.report
    assert "func_data" in benchy.report
    assert "async_test" in benchy.report

    # assert that functions were registered
    assert "func_add" in stakk.stack.get_stack(stack_id)
    assert "func_minus" in stakk.stack.get_stack(stack_id)
    assert "func_data" in stakk.stack.get_stack(stack_id)
    assert "async_test" in stakk.stack.get_stack(stack_id)

    # clear global registers
    stakk.benchy.report = {}
    stakk.stack.funcs = {}