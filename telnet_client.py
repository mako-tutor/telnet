#!/usr/bin/env python3
import telnetlib
import time
import re
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class TelnetConfig:
    host: str
    port: int = 23
    timeout: float = 10.0
    encoding: str = 'utf-8'
    debug: bool = False

class TelnetScript:
    def __init__(self, config: TelnetConfig):
        self.config = config
        self.tn = None
        self.logger = self._setup_logger()
        self.commands = []
        
    def _setup_logger(self):
        logger = logging.getLogger('telnet_script')
        if self.config.debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def connect(self) -> bool:
        try:
            self.tn = telnetlib.Telnet(self.config.host, self.config.port, self.config.timeout)
            self.logger.debug(f"Connected to {self.config.host}:{self.config.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.tn:
            self.tn.close()
            self.logger.debug("Disconnected")
    
    def send_command(self, command: str, expect: Optional[str] = None, timeout: float = 5.0) -> str:
        if not self.tn:
            raise ConnectionError("Not connected to telnet server")
        
        self.logger.debug(f"Sending command: {command}")
        self.tn.write(command.encode(self.config.encoding) + b'\n')
        
        if expect:
            try:
                index, match, text = self.tn.expect([expect.encode(self.config.encoding)], timeout)
                response = text.decode(self.config.encoding, errors='ignore')
                self.logger.debug(f"Expected pattern found: {expect}")
                return response
            except Exception as e:
                self.logger.error(f"Failed to find expected pattern '{expect}': {e}")
                return ""
        else:
            time.sleep(0.5)
            response = self.tn.read_very_eager().decode(self.config.encoding, errors='ignore')
            self.logger.debug(f"Response: {response}")
            return response
    
    def wait_for(self, pattern: str, timeout: float = 10.0) -> str:
        if not self.tn:
            raise ConnectionError("Not connected to telnet server")
        
        try:
            index, match, text = self.tn.expect([pattern.encode(self.config.encoding)], timeout)
            response = text.decode(self.config.encoding, errors='ignore')
            self.logger.debug(f"Pattern '{pattern}' found")
            return response
        except Exception as e:
            self.logger.error(f"Pattern '{pattern}' not found within {timeout}s: {e}")
            return ""
    
    def read_until(self, pattern: str, timeout: float = 10.0) -> str:
        if not self.tn:
            raise ConnectionError("Not connected to telnet server")
        
        try:
            response = self.tn.read_until(pattern.encode(self.config.encoding), timeout)
            decoded_response = response.decode(self.config.encoding, errors='ignore')
            self.logger.debug(f"Read until '{pattern}': {decoded_response}")
            return decoded_response
        except Exception as e:
            self.logger.error(f"Failed to read until '{pattern}': {e}")
            return ""
    
    def login(self, username: str, password: str, 
              username_prompt: str = "login:", 
              password_prompt: str = "Password:",
              success_pattern: str = "$") -> bool:
        try:
            self.wait_for(username_prompt)
            self.send_command(username)
            
            self.wait_for(password_prompt)
            self.send_command(password)
            
            response = self.wait_for(success_pattern)
            if success_pattern in response:
                self.logger.debug("Login successful")
                return True
            else:
                self.logger.error("Login failed")
                return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def execute_script(self, script_commands: List[Dict[str, Any]]) -> List[str]:
        results = []
        for cmd_dict in script_commands:
            cmd = cmd_dict.get('command', '')
            expect = cmd_dict.get('expect')
            timeout = cmd_dict.get('timeout', 5.0)
            delay = cmd_dict.get('delay', 0)
            
            if delay > 0:
                time.sleep(delay)
            
            if cmd:
                response = self.send_command(cmd, expect, timeout)
                results.append(response)
                
                if 'condition' in cmd_dict:
                    condition = cmd_dict['condition']
                    if not self._check_condition(response, condition):
                        self.logger.warning(f"Condition failed for command: {cmd}")
                        if cmd_dict.get('stop_on_fail', False):
                            break
        
        return results
    
    def _check_condition(self, response: str, condition: Dict[str, Any]) -> bool:
        condition_type = condition.get('type', 'contains')
        pattern = condition.get('pattern', '')
        
        if condition_type == 'contains':
            return pattern in response
        elif condition_type == 'regex':
            return bool(re.search(pattern, response))
        elif condition_type == 'not_contains':
            return pattern not in response
        else:
            return True

class TelnetScriptBuilder:
    def __init__(self, config: TelnetConfig):
        self.config = config
        self.script = TelnetScript(config)
        self.commands = []
    
    def add_command(self, command: str, expect: Optional[str] = None, 
                   timeout: float = 5.0, delay: float = 0) -> 'TelnetScriptBuilder':
        cmd_dict = {
            'command': command,
            'expect': expect,
            'timeout': timeout,
            'delay': delay
        }
        self.commands.append(cmd_dict)
        return self
    
    def add_condition(self, condition_type: str = 'contains', 
                     pattern: str = '', stop_on_fail: bool = False) -> 'TelnetScriptBuilder':
        if self.commands:
            self.commands[-1]['condition'] = {
                'type': condition_type,
                'pattern': pattern
            }
            self.commands[-1]['stop_on_fail'] = stop_on_fail
        return self
    
    def add_login(self, username: str, password: str,
                  username_prompt: str = "login:",
                  password_prompt: str = "Password:",
                  success_pattern: str = "$") -> 'TelnetScriptBuilder':
        self.login_info = {
            'username': username,
            'password': password,
            'username_prompt': username_prompt,
            'password_prompt': password_prompt,
            'success_pattern': success_pattern
        }
        return self
    
    def run(self) -> List[str]:
        if not self.script.connect():
            return []
        
        try:
            if hasattr(self, 'login_info'):
                login_success = self.script.login(**self.login_info)
                if not login_success:
                    return []
            
            results = self.script.execute_script(self.commands)
            return results
        finally:
            self.script.disconnect()

def create_telnet_script(host: str, port: int = 23, **kwargs) -> TelnetScriptBuilder:
    config = TelnetConfig(host=host, port=port, **kwargs)
    return TelnetScriptBuilder(config)

if __name__ == "__main__":
    script = create_telnet_script("localhost", debug=True)
    
    results = (script
               .add_login("admin", "password")
               .add_command("show version", expect="$")
               .add_command("show interfaces", expect="$")
               .add_condition("contains", "FastEthernet", stop_on_fail=True)
               .add_command("exit")
               .run())
    
    for i, result in enumerate(results):
        print(f"Command {i+1} result: {result}")