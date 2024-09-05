import os

import paramiko
import time
import pandas as pd
import asyncio


def send_cmd(ssh, cmd, wait_str, timeout=10):
    # 发送命令并回车
    ssh.send(cmd + '\n')
    time.sleep(1)
    buff = ''
    print(f"  开始执行命令：{cmd}")
    for i in range(120):
        # 等待预期结束字符出现
        if wait_str in buff:
            print(f"\n    命令执行成功")
            return True
        print(f"还未等到{wait_str}, i={i}, buffer={buff}，继续")
        resp = ssh.recv(9999)
        buff += resp.decode('utf-8')
        time.sleep(1)
        print("\r", end="")
        print(f"    等待返回结果: {i}s", end="", flush=True)
    print(f"\n    命令执行超时")
    return False


async def execute_cmd(ip, user, passwd, port, root_user, root_passwd, command):
    try:
        print(f'> {user} -> {ip}')
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(ip, port, user, passwd, timeout=3)

        ssh = s.invoke_shell()
        time.sleep(1)

        # 设置单次命令执行超时时间，10s
        ssh.settimeout(10)

        # 切换root用户
        if user != "root":
            print("当前用户不为root，执行切换")
            # 切换root用户
            if not send_cmd(ssh, f'su - {root_user}', 'Password: '):
                print("切换用户失败")
                s.close()
                return
            # 输入root密码
            if not send_cmd(ssh, root_passwd, '# '):
                print("输入密码失败")
                s.close()
                return
        # 执行命令
        if not send_cmd(ssh, command, '# '):
            print("下发命令失败")
            s.close()
            return
        # 关闭ssh通道
        s.close()
        print('执行完毕...')
    except Exception as e:
        print('\n\033[31m执行失败...\033[0m')
        print(e)
    return


def get_host_list():
    sheet = pd.read_excel(os.path.split(os.path.realpath(__file__))[0] + '/info.xlsx', engine="openpyxl",
                          sheet_name="hosts")
    if not sheet:
        return []
    return sheet.values


def get_host_list_from_csv():
    return [
                ("neteco", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12", "bash /opt/lab/asyncio/slow_script.sh", "Y"),
                ("neteco", "10.43.70.177", "ossadm", "PRov+-12", "root", "PRov+-12", "bash /opt/lab/asyncio/slow_script.sh", "Y")
        ]
    # return [('iit-v2', '8.100.93.249', 'root' 'cjqG@02hQ0LZ9ea', 'root' 'cjqG@02hQ0LZ9ea', 'curl -s http://wangzhihong.obs.br-iaas-icsl1.myhuaweicloud.com/run.sh |bash -s iit-v2  8.100.93.249', 'Y')]


def main():
    # hosts = get_host_list()
    hosts = get_host_list_from_csv()
    for m in hosts:
        hostname = m[0]
        ip = m[1]
        user = m[2]
        passwd = m[3]
        root_user = m[4]
        root_passwd = m[5]
        command = m[6]
        is_need_scan = m[7]
        if is_need_scan.lower() != 'y':
            continue
        print(m)
        execute_cmd(ip, user, passwd, 22, root_user, root_passwd, command)


if __name__ == '__main__':
    main()
