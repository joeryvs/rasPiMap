from multiprocessing import Pool
import datetime
import asyncio

async def fetch_test(number) -> str:

    print("before %d" % number)
    await asyncio.sleep(2.5)
    print("after %d" % number)
    return "\t  https::/localhost/?id=%d     \n" % number

def call_number(i):
    return asyncio.run(fetch_test(i))

def multi_test(start,end) -> list[str]:
    vals = []
    with Pool(10) as p:
        tasks = p.map_async(call_number,range(start,end),callback=vals.append,error_callback=vals.append)

        while not tasks.ready():
            print(datetime.datetime.now())
            tasks.wait(0.5)

    return vals

async def fetch_all(start,end) -> list[str]:

    async def task(i : int) -> str:
        t = await fetch_test(i)
        return t.strip()
    await asyncio.sleep(0.1)
    values = (i for i in range(start,end))
    # tasks = [task(i) for i in values]
    vals = []
    with Pool(10) as p:
        tasks = p.map_async(task,values,20,vals.append,vals.append)
    while not tasks.ready():
        print(datetime.datetime.now())
        tasks.wait(4)
        print(vals)
    print(vals)
    print(tasks)

    # result = [await t for t in tasks]
    
    # result = asyncio.as_completed(tasks,timeout=300)
    # async for r in result:
    #     await r
    # result = [await r for r in result]
    # return result

def main():
    # asyncio.run(fetch_all(50,80))
    multi_test(40,90)


if __name__ == "__main__":
    main()

