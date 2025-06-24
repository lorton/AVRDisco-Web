import telnetlib
import threading
import time
import logging

class AVRController:
    def __init__(self, host, port, timeout=5, debug_mode=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = None
        self.connected = False
        self.lock = threading.Lock()
        self.debug_mode = debug_mode
        
    def connect(self):
        """Connect to the AV receiver"""
        if self.debug_mode:
            self.connected = True
            print(f"[DEBUG] Simulating connection to AVR at {self.host}:{self.port}")
            return True
            
        try:
            with self.lock:
                if self.connection:
                    self.disconnect()
                
                self.connection = telnetlib.Telnet(self.host, self.port, self.timeout)
                self.connected = True
                logging.info(f"Connected to AVR at {self.host}:{self.port}")
                return True
        except Exception as e:
            logging.error(f"Failed to connect to AVR: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the AV receiver"""
        if self.debug_mode:
            self.connected = False
            print("[DEBUG] Simulating disconnect from AVR")
            return
            
        try:
            with self.lock:
                if self.connection:
                    self.connection.close()
                    self.connection = None
                self.connected = False
                logging.info("Disconnected from AVR")
        except Exception as e:
            logging.error(f"Error disconnecting: {e}")
    
    def send_command(self, command):
        """Send a command to the AV receiver"""
        if not self.connected:
            if not self.connect():
                return False, "Not connected to AVR"
        
        if self.debug_mode:
            print(f"[DEBUG] Would send command: {command}")
            return True, "Debug mode - command printed"
        
        try:
            with self.lock:
                command_bytes = (command + '\r').encode('ascii')
                self.connection.write(command_bytes)
                logging.info(f"Sent command: {command}")
                return True, "Command sent"
        except Exception as e:
            logging.error(f"Failed to send command '{command}': {e}")
            self.connected = False
            return False, str(e)
    
    def read_response(self, timeout=2):
        """Read response from AV receiver"""
        if not self.connected:
            return None
            
        if self.debug_mode:
            return "DEBUG: Simulated response"
        
        try:
            with self.lock:
                response = self.connection.read_until(b'\r', timeout)
                if response:
                    decoded = response.decode('ascii').strip()
                    logging.info(f"Received response: {decoded}")
                    return decoded
        except Exception as e:
            logging.error(f"Failed to read response: {e}")
            self.connected = False
        return None
    
    def send_and_wait(self, command, wait_time=1):
        """Send command and wait for response - handles multi-line commands"""
        # Handle multi-line commands (separated by \n)
        commands = command.split('\n')
        responses = []
        
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
                continue
                
            success, message = self.send_command(cmd)
            if not success:
                return success, message
            
            time.sleep(wait_time)
            response = self.read_response()
            if response:
                responses.append(response)
        
        return True, '; '.join(responses) if responses else "Commands sent"