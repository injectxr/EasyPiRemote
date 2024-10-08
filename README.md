# EasyPiRemote

**EasyPiRemote**は、Paramikoライブラリを使用してRaspberry PiにSSH接続を行い、ローカルからリモートPi上でコマンドを実行するインターフェースを提供します。スクリプトは、コマンドをリモートで実行し、その結果をローカルシェルに出力することで、まるでローカルで実行しているかのような体験を擬似的に提供します。
## 機能
- Pythonファイル一つで動作
- Raspberry PiへのSSH接続
- Pythonスクリプトの擬似ローカル実行
- Raspberry Pi上のファイルのローカルマシンへのダウンロード
- ターミナル形式でのコマンド実行


## 必要なライブラリ
`paramiko`ライブラリを使用します。インストールされていない場合は以下のコマンドでインストールしてください:

```bash
pip install paramiko
```
## 使い方
Step 1: 接続情報を設定
`setup.py`ファイル内で、以下の変数に必要な接続情報を設定します:

`hostname`: Raspberry Piのホスト名またはIPアドレス（例: raspberrypi.local）<br>
`username`: Raspberry Piのユーザー名（デフォルトではpi）<br>
`password`: Raspberry Piのパスワード（デフォルトではraspberry）<br>

```python
hostname = 'raspberrypi.local'  # Raspberry Piのホスト名またはIPアドレス
username = 'pi'                 # Raspberry Piのユーザー名
password = 'yourpass'           # パスワード

```
Step 2: プログラムの実行
プログラムを実行するには、ターミナルで以下のコマンドを入力します:
```bash
python setup.py
```
Step 3: コマンドを使用した操作

1. **ローカルのPythonスクリプトを擬似的にリモートで実行**
   ローカルのPythonファイルをRaspberry Piにアップロードし、リモートで実行して、その結果をシェルGUIに表示します。
   次のコマンドを使用します:
```Terminal
pi <ファイル名>.py
```
![5205d318217fd410886ca6d3561fe014](https://github.com/user-attachments/assets/9dc6e942-d944-48cc-b028-17e35145a05f)


2. リモートファイルのダウンロード
Raspberry Pi上のファイルをローカルにダウンロードするには、次のコマンドを使用します:

```Terminal
get <リモートファイル名>.py
```

3. 一般的なコマンド
通常のターミナルコマンド（例: cd、ls）も直接入力して実行できます。

4. 終了
プログラムを終了するには、以下のコマンドを使用します:
```Terminal
exit
```




注意事項
Raspberry Piの電源が入っていて、ネットワークに接続されている必要があります。
sudoコマンドを使う場合は、パスワード入力が求められることがあります。
