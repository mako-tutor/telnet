#!/usr/bin/env python3
from telnet_client import create_telnet_script, TelnetConfig, TelnetScript

def example_cisco_router():
    """Ciscoルーターに接続してコマンドを実行する例"""
    print("=== Cisco Router Example ===")
    
    script = create_telnet_script("192.168.1.1", debug=True)
    
    results = (script
               .add_login("admin", "cisco123", 
                         username_prompt="Username:", 
                         password_prompt="Password:",
                         success_pattern="#")
               .add_command("terminal length 0", expect="#")
               .add_command("show version", expect="#")
               .add_condition("contains", "IOS", stop_on_fail=True)
               .add_command("show ip interface brief", expect="#")
               .add_command("show running-config", expect="#")
               .add_command("exit")
               .run())
    
    for i, result in enumerate(results):
        print(f"Command {i+1} result:\n{result}\n" + "="*50)

def example_linux_server():
    """Linuxサーバーに接続してシステム情報を取得する例"""
    print("=== Linux Server Example ===")
    
    script = create_telnet_script("10.0.0.100", debug=True)
    
    results = (script
               .add_login("root", "password123")
               .add_command("uname -a", expect="$", timeout=3.0)
               .add_command("df -h", expect="$")
               .add_condition("contains", "/", stop_on_fail=False)
               .add_command("free -m", expect="$")
               .add_command("ps aux | head -20", expect="$")
               .add_command("exit")
               .run())
    
    for i, result in enumerate(results):
        print(f"Command {i+1} result:\n{result}\n" + "="*50)

def example_network_switch():
    """ネットワークスイッチの設定変更例"""
    print("=== Network Switch Configuration Example ===")
    
    script = create_telnet_script("192.168.10.1", debug=True)
    
    results = (script
               .add_login("admin", "switch123", success_pattern=">")
               .add_command("enable", expect="Password:")
               .add_command("enable_password", expect="#")
               .add_command("configure terminal", expect="(config)#")
               .add_command("interface fastethernet 0/1", expect="(config-if)#")
               .add_command("description 'Server Port'", expect="(config-if)#")
               .add_command("no shutdown", expect="(config-if)#")
               .add_command("exit", expect="(config)#")
               .add_command("exit", expect="#")
               .add_command("write memory", expect="#")
               .add_condition("contains", "OK", stop_on_fail=True)
               .add_command("exit")
               .run())
    
    for i, result in enumerate(results):
        print(f"Command {i+1} result:\n{result}\n" + "="*50)

def example_custom_script():
    """カスタムスクリプトの例 - より高度な制御"""
    print("=== Custom Script Example ===")
    
    config = TelnetConfig(
        host="192.168.1.10",
        port=23,
        timeout=15.0,
        debug=True,
        encoding='utf-8'
    )
    
    script = TelnetScript(config)
    
    if script.connect():
        try:
            script.wait_for("login:")
            script.send_command("admin")
            
            script.wait_for("Password:")
            script.send_command("admin123")
            
            response = script.wait_for("$")
            if "$" in response:
                print("Login successful!")
                
                script.send_command("show system status")
                status_output = script.read_until("$", timeout=10)
                print(f"System status:\n{status_output}")
                
                if "OK" in status_output:
                    print("System is healthy, proceeding with backup...")
                    script.send_command("backup config")
                    backup_result = script.wait_for("Complete", timeout=30)
                    print(f"Backup result: {backup_result}")
                else:
                    print("System not healthy, skipping backup")
                
                script.send_command("logout")
            else:
                print("Login failed!")
        
        finally:
            script.disconnect()

def example_error_handling():
    """エラーハンドリングの例"""
    print("=== Error Handling Example ===")
    
    try:
        script = create_telnet_script("invalid.host.com", timeout=5.0, debug=True)
        results = (script
                   .add_login("user", "pass")
                   .add_command("test command")
                   .run())
        
        if not results:
            print("Connection or execution failed")
        
    except Exception as e:
        print(f"Error occurred: {e}")

def example_conditional_logic():
    """条件分岐ロジックの例"""
    print("=== Conditional Logic Example ===")
    
    script = create_telnet_script("192.168.1.1", debug=True)
    
    results = (script
               .add_login("admin", "password")
               .add_command("show interfaces", expect="#")
               .add_condition("regex", r"FastEthernet\d+/\d+ is up", stop_on_fail=False)
               .add_command("show ip route", expect="#")
               .add_condition("not_contains", "0.0.0.0", stop_on_fail=True)
               .add_command("ping 8.8.8.8", expect="#", timeout=10.0)
               .add_condition("contains", "Success rate is 100", stop_on_fail=False)
               .add_command("exit")
               .run())
    
    for i, result in enumerate(results):
        print(f"Command {i+1} result:\n{result}\n" + "="*50)

if __name__ == "__main__":
    print("Telnet Client Examples")
    print("Choose an example to run:")
    print("1. Cisco Router")
    print("2. Linux Server") 
    print("3. Network Switch")
    print("4. Custom Script")
    print("5. Error Handling")
    print("6. Conditional Logic")
    
    try:
        choice = input("Enter choice (1-6): ")
        
        if choice == "1":
            example_cisco_router()
        elif choice == "2":
            example_linux_server()
        elif choice == "3":
            example_network_switch()
        elif choice == "4":
            example_custom_script()
        elif choice == "5":
            example_error_handling()
        elif choice == "6":
            example_conditional_logic()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")