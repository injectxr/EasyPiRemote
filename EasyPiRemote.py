# EasyPiRemote使い方

# Step 1: 必要な外部ライブラリをインストール
# 以下のコマンドを使用して、Paramikoをインストールします。
# ターミナルで次のコマンドを実行:
# > pip install paramiko

# Step 2: 接続情報を設定
# hostname、username、passwordをスクリプト内で設定してください
# これにより、Raspberry PiへのSSH接続が可能になります

# Step 3: `setup.py`を実行
# 以下のコマンドを使って、スクリプトを実行してください
# > python setup.py

# Step 4: 基本的な操作
# ターミナルと同じ形式のコマンドを使用して、
# ファイル移動や表示ができます（例: cd、ls など）

# -----------------------------------------------------------------------------

# ディレクトリの区別

# ローカルディレクトリ: 
# - Windows上のファイルやフォルダを指します。

# リモートディレクトリ: 
# - Raspberry Pi上のファイルやフォルダを指します。

# -----------------------------------------------------------------------------

# 実行方法

# 1. プログラムを実行
# ローカルディレクトリのファイルを指定して実行します。
# setup.pyから見て、ファイル名を入力します。
# 例: `> pi <ファイル名>.py`

# プログラムの停止
# ctrl + c

# 2. ファイルのダウンロード
# リモートディレクトリ（Raspberry Pi上）からファイルをダウンロードするには、
# 現在のディレクトリの相対パスを指定して実行します。
# 例1: `> cd program` → `get <ファイル名>.py`
# 例2: `> get program/<ファイル名>.py`


import paramiko
import time
import os

hostname = 'raspberrypi.local'  # Raspberry Piのホスト名またはIPアドレス
username = 'pi'                 # Raspberry Piのユーザー名
password = ''          # パスワード

def main():
    session = ssh_connect_and_interactive(hostname, username, password)
    if session:
        client(session)

def client(session):
    shell = session.invoke_shell()
    time.sleep(1)

    if shell.recv_ready():
        shell.recv(1024).decode('utf-8')
        print("接続成功")

    while True:
        command = input("> ")

        # シャットダウン
        if command.lower() == 'exit':
            print("接続を終了します...")
            shell.send("sudo shutdown -h now" + '\n')
            time.sleep(100)
            break

        # pi ~~~.py - ローカルディレクトリのファイル名を入力
        if command.lower().startswith('pi '):
            file_name = command.split()[1]
            local_file_path = os.path.join(os.getcwd(), file_name)

            current_directory = get_current_directory(shell)
            if current_directory is None:
                print("カレントディレクトリの取得に失敗しました。")
                continue

            remote_file_path = current_directory + '/' + file_name
            upload_file(session, local_file_path, remote_file_path)
            run_remote_python(shell, remote_file_path)
            continue

        # get ~~~.py リモートディレクトリのファイル名を入力
        if command.lower().startswith('get '):
            file_name = command.split()[1]
            current_directory = get_current_directory(shell)
            remote_file_path = current_directory + '/' + file_name
            local_file_path = os.path.join(os.getcwd(), file_name)
            download_file(session, remote_file_path, local_file_path)
            print(f"{remote_file_path} を {local_file_path} に保存しました")
            continue

        shell.send(command + '\n')
        time.sleep(1.5)
        while shell.recv_ready():
            output = shell.recv(1024).decode('utf-8')
            print(output)

def ssh_connect_and_interactive(hostname, username, password):
    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"{hostname} に接続中...")
        session.connect(hostname, username=username, password=password)
        return session
    except Exception as e:
        print(f"接続エラー: {e}")
        session.close()
        return None

def get_current_directory(shell):
    shell.send('pwd\n')
    time.sleep(1.5)
    output = shell.recv(1024).decode('utf-8').splitlines()
    for line in output:
        if line.startswith('/'):
            return line.strip()
    return None

def upload_file(session, local_file_path, remote_file_path):
    try:
        sftp = session.open_sftp()
        sftp.put(local_file_path, remote_file_path)
        
        print(f"ファイルがリモートにアップロードされました: {remote_file_path}")
        sftp.close()
    except Exception as e:
        print(f"ファイルアップロードエラー: {e}")

def run_remote_python(shell, remote_file_path):
    print(f"python3 {remote_file_path} を実行中...")
    shell.send(f'python3 {remote_file_path}\n')

    try:
        while True:
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                print(output, end='')
    except KeyboardInterrupt:
        print("\n実行を終了しました。")
    
if __name__ == "__main__":
    main()
