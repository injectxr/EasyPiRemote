# EasyPiRemote

**EasyPiRemote**は、Raspberry PiをSSH経由でリモート操作できるシンプルなPythonツールです。Pythonファイル一つで動作し、コマンドを使ってRaspberry Piへのファイル転送やPythonスクリプトの実行、リモートファイルのダウンロードが簡単に行えます。

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
1. ローカルのPythonファイルをアップロードして実行
**EasyPiRemote**を使用して、ローカルのPythonファイルをRaspberry Piにアップロードし、その場で実行することができます。コマンド形式は以下の通りです:

```Terminal
pi <ファイル名>.py
```

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
