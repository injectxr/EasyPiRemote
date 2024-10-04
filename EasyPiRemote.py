import paramiko
import time
import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext

hostname = 'raspberrypi.local'  # Raspberry Piのホスト名またはIPアドレス
username = 'pi'                 # Raspberry Piのユーザー名
password = 'raspberry'          # パスワード

def main():
    os.system("cls")
    session = ssh_connect_and_interactive(hostname, username, password)
    if session:
        client(session)

def client(session):
    original_shell = session.invoke_shell() 
    time.sleep(1)

    if original_shell.recv_ready():
        original_shell.recv(1024).decode('utf-8')
        print("\033[92m[ezPi] : 接続成功\033[0m")
    
    command = ""
    current_directory = get_current_directory(original_shell)
    prompt = f"{username}@raspberrypi:{current_directory}$ "

    while True:
        command = input(f"\033[92m{prompt}\033[0m")

        if command.lower() == 'exit':
            print("\033[93m[ezPi] : 接続を終了します...\033[0m")  
            original_shell.send("sudo shutdown -h now" + '\n')
            time.sleep(100)
            break

        if command.lower().startswith('pi '):
            file_name = command.split()[1]
            local_file_path = os.path.join(os.getcwd(), file_name)

            current_directory = get_current_directory(original_shell)
            if current_directory is None:
                print("\033[91m[ezPi] : カレントディレクトリの取得に失敗しました。\033[0m")  
                continue

            remote_file_path = current_directory + '/' + file_name
            if upload_file(session, local_file_path, remote_file_path):
                copy_shell = session.invoke_shell() 
                try:
                    run_remote_python(copy_shell, remote_file_path,file_name)
                finally:
                    copy_shell.close()
            continue

        if command.lower().startswith('get '):
            file_name = command.split()[1]
            current_directory = get_current_directory(original_shell)
            if current_directory is None:
                print("\033[91m[ezPi] : カレントディレクトリの取得に失敗しました。\033[0m")
                continue

            remote_file_path = current_directory + '/' + file_name
            local_file_path = os.path.join(os.getcwd(), file_name)
            download_file(session, remote_file_path, local_file_path)
            print(f"\033[92m[ezPi] : {remote_file_path} を {local_file_path} に保存しました\033[0m") 
            continue

        original_shell.send(command + '\n')
        time.sleep(1.5)

        if command.startswith("cd "):
            new_directory = get_current_directory(original_shell)
            if new_directory:
                prompt = f"{username}@raspberrypi:{new_directory}$ "  

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

def run_remote_python(shell, remote_file_path,file_name):
    
    def is_scrolled_to_bottom(terminal_o):
        return terminal_o.yview()[1] >= 0.95

    root, terminal_output, closed = create_terminal_window(file_name)
    shell.send(f'python3 {remote_file_path}\n')
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    try:
        buffer = []
        while not closed[0]:
            if shell.recv_ready():
                data = shell.recv(1024).decode('utf-8')
                buffer.append(data)  

                combined_buffer = ''.join(buffer)  
                while "\n" in combined_buffer:
                    line, combined_buffer = combined_buffer.split("\n", 1)
                    buffer = [combined_buffer]  
                    clean_line = ansi_escape.sub('', line).strip()
                    terminal_output.insert(tk.END, clean_line + "\n")
                    if is_scrolled_to_bottom(terminal_output):
                        terminal_output.see(tk.END)

                    terminal_output.update_idletasks()

            if not closed[0]:
                try:
                    root.update()  
                except tk.TclError:
                    break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if not closed[0]: 
            root.destroy()
            return 0

def create_terminal_window(file_name):
    root = tk.Tk()
    root.title("Terminal")
    closed = [False]
    def on_close():
        closed[0] = True
        try:
            root.quit()  
            root.destroy()  
        except tk.TclError:
            pass  
        
    window_width = 800
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    title_bar = tk.Frame(root, bg="gray", relief="raised")
    title_bar.pack(side=tk.TOP, fill=tk.X)
    title_label = tk.Label(title_bar, text=f"ezPi Terminal - {file_name}", bg="gray", fg="white", padx=10)
    title_label.pack(side=tk.LEFT, pady=2)
    window_controls = tk.Frame(title_bar, bg="gray")
    window_controls.pack(side=tk.RIGHT)
    close_button = tk.Button(window_controls, text="×", command=on_close, bg="gray", fg="white", bd=0, activebackground="red", activeforeground="white")
    close_button.pack(side=tk.LEFT, padx=2, pady=2)
    terminal_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    terminal_output.pack(padx=0, pady=0)
    terminal_output.configure(font=("Cascadia Mono", 10), bg="#002b36", fg="white")
    terminal_output.tag_configure("indent", lmargin1=10, lmargin2=10)

    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def on_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        new_x = root.winfo_x() + deltax
        new_y = root.winfo_y() + deltay
        root.geometry(f"+{new_x}+{new_y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", on_move)
    return root, terminal_output, closed

def ssh_connect_and_interactive(hostname, username, password):
    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\033[92m[ezPi] : \033[0m{hostname} に接続中...") 
        session.connect(hostname, username=username, password=password)
        return session
    except Exception as e:
        print(f"\033[91m[ezPi] : 接続エラー: {e}\033[0m") 
        session.close()
        return None

def upload_file(session, local_file_path, remote_file_path):
    try:
        sftp = session.open_sftp()
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        return True
    
    except Exception as e:
        print(f"\033[91m[ezPi] : ファイルアップロードエラー: {e}\033[0m")  
        return False

def download_file(session, remote_file_path, local_file_path):
    try:
        sftp = session.open_sftp()
        try:
            sftp.stat(remote_file_path) 
            print(f"\033[93m[ezPi] : リモートファイル {remote_file_path} をダウンロード中...\033[0m")  
        except FileNotFoundError:
            print(f"\033[91m[ezPi] : リモートファイル {remote_file_path} が存在しません。\033[0m")  
            sftp.close()
            return
        sftp.get(remote_file_path, local_file_path)
        print(f"\033[92m[ezPi] : ファイルが {local_file_path} に保存されました。\033[0m")  
        sftp.close()
    except Exception as e:
        print(f"\033[91m[ezPi] : ファイル転送エラー: {e}\033[0m") 
if __name__ == "__main__":
    main()
    
