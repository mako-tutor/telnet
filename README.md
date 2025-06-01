# Python Telnet Client with Scripting Support

シンプルで使いやすいPython Telnetクライアントライブラリです。ネットワーク機器やサーバーへの自動接続とコマンド実行をスクリプトで簡単に記述できます。

## 特徴

- 🔌 **簡単接続**: ホストとポートを指定するだけで接続
- 📝 **スクリプト記述**: メソッドチェーンで直感的なスクリプト作成
- 🔍 **条件分岐**: 応答内容に基づく条件分岐処理
- 🔐 **認証サポート**: ユーザー名/パスワード認証
- 📊 **ログ機能**: デバッグモードでの詳細ログ出力
- ⏱️ **タイムアウト制御**: コマンドごとのタイムアウト設定
- 🎯 **パターンマッチング**: 正規表現による応答パターンマッチング

## インストール

```bash
git clone https://github.com/mako-tutor/telnet.git
cd telnet
```

このライブラリは標準ライブラリのみを使用しているため、追加のインストールは不要です。

## 基本的な使用方法

### シンプルな例

```python
from telnet_client import create_telnet_script

# 基本的な接続とコマンド実行
script = create_telnet_script("192.168.1.1", debug=True)

results = (script
           .add_login("admin", "password")
           .add_command("show version", expect="#")
           .add_command("show interfaces", expect="#")
           .add_command("exit")
           .run())

for result in results:
    print(result)
```

### 条件分岐を使用した例

```python
from telnet_client import create_telnet_script

script = create_telnet_script("192.168.1.1")

results = (script
           .add_login("admin", "password")
           .add_command("show interfaces", expect="#")
           .add_condition("contains", "FastEthernet", stop_on_fail=True)
           .add_command("show ip route", expect="#")
           .add_condition("regex", r"\\d+\\.\\d+\\.\\d+\\.\\d+", stop_on_fail=False)
           .add_command("exit")
           .run())
```

## API リファレンス

### TelnetConfig

接続設定を管理するデータクラス

```python
@dataclass
class TelnetConfig:
    host: str              # 接続先ホスト
    port: int = 23         # ポート番号（デフォルト: 23）
    timeout: float = 10.0  # 接続タイムアウト
    encoding: str = 'utf-8' # 文字エンコーディング
    debug: bool = False    # デバッグモード
```

### TelnetScriptBuilder

スクリプトビルダーのメインクラス

#### メソッド

- `add_command(command, expect=None, timeout=5.0, delay=0)`: コマンドを追加
- `add_condition(condition_type='contains', pattern='', stop_on_fail=False)`: 条件を追加
- `add_login(username, password, username_prompt='login:', password_prompt='Password:', success_pattern='$')`: ログイン情報を設定
- `run()`: スクリプトを実行

#### 条件タイプ

- `contains`: 指定した文字列が含まれているかチェック
- `not_contains`: 指定した文字列が含まれていないかチェック
- `regex`: 正規表現でパターンマッチング

### TelnetScript

低レベルAPI - より細かい制御が必要な場合

```python
from telnet_client import TelnetScript, TelnetConfig

config = TelnetConfig(host="192.168.1.1", debug=True)
script = TelnetScript(config)

if script.connect():
    script.send_command("show version")
    response = script.read_until("#", timeout=10)
    script.disconnect()
```

## 使用例

### Ciscoルーター設定

```python
def configure_cisco_router():
    script = create_telnet_script("192.168.1.1", debug=True)
    
    results = (script
               .add_login("admin", "cisco123", 
                         username_prompt="Username:", 
                         password_prompt="Password:",
                         success_pattern="#")
               .add_command("configure terminal", expect="(config)#")
               .add_command("interface fastethernet 0/1", expect="(config-if)#")
               .add_command("ip address 192.168.10.1 255.255.255.0", expect="(config-if)#")
               .add_command("no shutdown", expect="(config-if)#")
               .add_command("exit", expect="(config)#")
               .add_command("exit", expect="#")
               .add_command("write memory", expect="#")
               .add_condition("contains", "OK", stop_on_fail=True)
               .run())
    
    return results
```

### Linuxサーバー監視

```python
def monitor_linux_server():
    script = create_telnet_script("10.0.0.100")
    
    results = (script
               .add_login("root", "password")
               .add_command("uptime", expect="$")
               .add_command("df -h", expect="$")
               .add_condition("not_contains", "100%", stop_on_fail=False)
               .add_command("free -m", expect="$")
               .add_command("ps aux | head -10", expect="$")
               .run())
    
    return results
```

## エラーハンドリング

```python
try:
    script = create_telnet_script("invalid.host.com", timeout=5.0)
    results = script.add_login("user", "pass").run()
    
    if not results:
        print("接続または実行に失敗しました")
        
except ConnectionError as e:
    print(f"接続エラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## デバッグ

デバッグモードを有効にすると、詳細なログが出力されます：

```python
script = create_telnet_script("192.168.1.1", debug=True)
```

出力例：
```
2023-12-01 10:30:00,123 - DEBUG - Connected to 192.168.1.1:23
2023-12-01 10:30:01,456 - DEBUG - Sending command: show version
2023-12-01 10:30:02,789 - DEBUG - Expected pattern found: #
```

## ライセンス

MIT License

## 貢献

1. このリポジトリをフォーク
2. 新しい機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。

---

**注意**: このライブラリはtelnetプロトコルを使用します。セキュリティが重要な環境では、SSHの使用を検討してください。