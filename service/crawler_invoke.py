import json
import time
import random
import threading
from collections import Counter
from multiprocessing.pool import ThreadPool

from tencentserverless import scf
from tencentserverless.exception import TencentServerlessSDKException
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

REGION = "ap-guangzhou"  # 地域


def invoke(func_name: str, data: dict, client: scf.Client, namespace: str, taskid: int, thrLock: threading.Lock):
    with thrLock:
        print(f"Invoke task: {taskid}")
    time.sleep(random.randint(1, 8) / 10)
    try:
        data = client.invoke(function_name=func_name, namespace=namespace, data=data)
    except TencentServerlessSDKException as e:
        print(e)
        data = None
    except TencentCloudSDKException as e:
        print(e)
        data = None
    return data


if __name__ == '__main__':
    with open("config/tencentKey.json") as fp:
        tencentKey = json.load(fp)
    with open("config/scf.json") as fp:
        scfConfig = json.load(fp)
    client = scf.Client(secret_id=tencentKey["SecretId"], secret_key=tencentKey["SecretKey"], region=REGION)

    args = []
    lock = threading.Lock()
    for i in range(100):
        args.append(("iper", {"data": "d"}, client, scfConfig["namespaces"]["crawler"], i, lock))
    start = time.perf_counter()
    with ThreadPool(10) as pool:
        res = pool.starmap(invoke, args)
    # print(res)
    usedtime = time.perf_counter() - start
    counter = Counter()
    for d in res:
        if d:
            info = json.loads(d)
            # print(info["ip"])
            counter.update({info["ip"]: 1})
    [print(f"{ip} [{i}]") for ip, i in counter.items()]
    print(f"Uptime: {round(usedtime, 3)}")
