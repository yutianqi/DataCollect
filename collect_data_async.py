import time
import os
import asyncio
import asyncssh
import pandas as pd

RESULT_MAP = {}


def get_scan_cmd(service, ip, login_user, login_pwd, execute_user, execute_pwd, command):
    # url = "http://wangzhihong.obs.br-iaas-icsl1.myhuaweicloud.com/run.sh"
    url = "https://myweb.obs.cn-north-7.ulanqab.huawei.com:5443/run.sh"
    script = url.split("/")[-1]
    if login_user == execute_user:
        return f"curl -s {url} | bash -s {service} {ip}"
    else:
        return f"wget --quiet {url} && echo {execute_pwd} | sudo -S bash {script} -s {service} {ip} && rm -f {script}"


async def execute_command_on_host(service, ip, login_user, login_pwd, execute_user, execute_pwd, command):
    host_key = f"{service}_{ip}"
    if command == "-":
        command = get_scan_cmd(service, ip, login_user, login_pwd, execute_user, execute_pwd, command)
    print(f"开始处理 {host_key}, 执行命令：{command} ...")
    try:
        async with asyncssh.connect(ip, username=login_user, password=login_pwd, known_hosts=None) as conn:
            # result = await conn.run(command, check=True)
            result = await conn.run(command)
            error = result.stderr.replace("[sudo] password for root:", "").strip()

            if not error:
                """
                if result.stdout:
                    print(result.stdout)
                print("finished")
                """
                RESULT_MAP[host_key] = (True, "")
            else:
                print(f"{host_key} 节点命令执行异常: {error}")
                RESULT_MAP[host_key] = (False, error)
    except Exception as exception:
        print(f"{host_key} 节点命令执行异常: {exception}")
        RESULT_MAP[host_key] = (False, str(exception))


async def execute_tasks(hosts):
    tasks = []
    for item in hosts:
        service = item[0]
        ip = item[1]
        login_user = item[2]
        login_pwd = item[3]
        execute_user = item[4]
        execute_pwd = item[5]
        command = item[6]
        is_need_scan = item[7]
        if is_need_scan.lower() != "y":
            continue
        tasks.append(
            execute_command_on_host(service, ip, login_user, login_pwd, execute_user, execute_pwd, command))

    await asyncio.gather(*tasks)


def get_host_list():
    sheet = pd.read_excel(os.path.split(os.path.realpath(__file__))[0] + '/info.xlsx', engine="openpyxl",
                          sheet_name="hosts")
    return sheet.values


def get_host_list_from_csv():
    """
    return [
        ("neteco1", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12",
         "echo PRov+-12 | sudo -S /opt/lab/asyncio/slow_script.sh", "Y"),
        ("neteco2", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12",
         "echo PRov+-12 | sudo -S /opt/lab/asyncio/slow_script.sh", "Y")
    ]

    return [
        ("iit-v2", "26.241.161.49", "opsadmin", "Hwsimg@srereqd2024", "root", "Hwsimg@srereqd2024", "", "Y")
    ]
    """
    return [
        ("neteco1", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12",
         "echo PRov+-12 | sudo -S /opt/lab/asyncio/slow_script.sh", "Y"),
        ("neteco2", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12",
         "echo PRov+-12 | sudo -S /opt/lab/asyncio/slow_script.sh1", "Y")
    ]


def save_result_to_file(filename="result.csv"):
    lines = ["Service,IP,Result,Desc\n"]
    with open(filename, "w+") as file_object:
        for key, value in RESULT_MAP.items():
            service = key.split("_")[0]
            ip = key.split("_")[1]
            status = value[0]
            description = value[1].replace("\r", "").replace("\n", "")
            lines.append(f"{service},{ip},{status},{description}\n")
        file_object.writelines(lines)


def main():
    hosts = get_host_list()
    # hosts = get_host_list_from_csv()
    # print(hosts)
    asyncio.run(execute_tasks(hosts))


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"执行完毕，耗时{int(end - start)}s，详情如下：")
    for key, value in RESULT_MAP.items():
        service = key.split("_")[0]
        ip = key.split("_")[1]
        status = value[0]
        description = value[1]
        print(f"{service}\t{ip}\t{status}\t{description}")
    filename = f"result_{int(time.time())}.csv"
    print(f"执行结果已保存到：{filename}")
    save_result_to_file(filename)


