import paramiko
import time
import os
import re

hostname = 'raspberrypi.local'  # Raspberry Piのホスト名またはIPアドレス
username = 'pi'                 # Raspberry Piのユーザー名
password = 'raspberry'          # パスワード

def main():
    session = ssh_connect_and_interactive(hostname, username, password)
    if session:
        client(session)

def client(session):
    original_shell = session.invoke_shell() 
    time.sleep(1)

    if original_shell.recv_ready():
        original_shell.recv(1024).decode('utf-8')
        print("\033[92mezPi:接続成功\033[0m")  # 緑色の接続成功メッセージ
    
    command = ""
    current_directory = get_current_directory(original_shell)
    prompt = f"{username}@raspberrypi:{current_directory}$ "

    while True:
        command = input(f"\033[92m{prompt}\033[0m")

        if command.lower() == 'exit':
            print("\033[93mezPi:接続を終了します...\033[0m")  # 黄色の終了メッセージ
            original_shell.send("sudo shutdown -h now" + '\n')
            time.sleep(100)
            break

        if command.lower().startswith('pi '):
            file_name = command.split()[1]
            local_file_path = os.path.join(os.getcwd(), file_name)

            current_directory = get_current_directory(original_shell)
            if current_directory is None:
                print("\033[91mezPi:カレントディレクトリの取得に失敗しました。\033[0m")  # 赤色のエラーメッセージ
                continue

            remote_file_path = current_directory + '/' + file_name
            if upload_file(session, local_file_path, remote_file_path):
                copy_shell = session.invoke_shell() 
                try:
                    run_remote_python(copy_shell, remote_file_path)
                finally:
                    copy_shell.close()
            continue

        if command.lower().startswith('get '):
            file_name = command.split()[1]
            current_directory = get_current_directory(original_shell)
            if current_directory is None:
                print("\033[91mezPi:カレントディレクトリの取得に失敗しました。\033[0m")
                continue

            remote_file_path = current_directory + '/' + file_name
            local_file_path = os.path.join(os.getcwd(), file_name)
            download_file(session, remote_file_path, local_file_path)
            print(f"\033[92mezPi:{remote_file_path} を {local_file_path} に保存しました\033[0m")  # 緑色の成功メッセージ
            continue

        original_shell.send(command + '\n')
        time.sleep(1.5)

        if command.startswith("cd "):
            new_directory = get_current_directory(original_shell)
            if new_directory:
                prompt = f"{username}@raspberrypi:{new_directory}$ "  # 新しいディレクトリを反映

        while original_shell.recv_ready():
            output = original_shell.recv(1024).decode('utf-8')
            output = re.sub(rf'{username}@raspberrypi:[^$]*\$ ', '', output)
            if output.strip():
                print(output, end='')


def get_current_directory(shell):
    shell.send('pwd\n')
    time.sleep(1.5)
    output = shell.recv(1024).decode('utf-8').splitlines()
    for line in output:
        if line.startswith('/'):
            return line.strip()  
    return None

def run_remote_python(shell, remote_file_path):
    shell.send(f'python3 {remote_file_path}\n')

    try:
        output = ""
        while True:
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                print(output, end='')
            if "Traceback" in output or "Error" in output:
                break 

            if "実行を終了しました。" in output:
                break

    except KeyboardInterrupt:
        print("\033[91m\nezPi:実行を強制終了しました。\033[0m")  # 赤色のエラーメッセージ
        shell.close()
        return 0

def ssh_connect_and_interactive(hostname, username, password):
    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"\033[92mezPi\033[0m:{hostname} に接続中...")  # 緑色の接続中メッセージ
        session.connect(hostname, username=username, password=password)
        return session
    except Exception as e:
        print(f"\033[91mezPi:接続エラー: {e}\033[0m")  # 赤色のエラーメッセージ
        session.close()
        return None

def upload_file(session, local_file_path, remote_file_path):
    try:
        sftp = session.open_sftp()
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        return True
    
    except Exception as e:
        print(f"\033[91mezPi:ファイルアップロードエラー: {e}\033[0m")  # 赤色のエラーメッセージ
        return False

def download_file(session, remote_file_path, local_file_path):
    try:
        sftp = session.open_sftp()
        try:
            sftp.stat(remote_file_path) 
            print(f"\033[93mezPi:リモートファイル {remote_file_path} をダウンロード中...\033[0m")  # 黄色の進行中メッセージ
        except FileNotFoundError:
            print(f"\033[91mezPi:リモートファイル {remote_file_path} が存在しません。\033[0m")  # 赤色のエラーメッセージ
            sftp.close()
            return
        sftp.get(remote_file_path, local_file_path)
        print(f"\033[92mezPi:ファイルが {local_file_path} に保存されました。\033[0m")  # 緑色の成功メッセージ
        sftp.close()
    except Exception as e:
        print(f"\033[91mezPi:ファイル転送エラー: {e}\033[0m")  # 赤色のエラーメッセージ

if __name__ == "__main__":
    main()
