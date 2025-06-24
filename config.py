import os
import argparse

class Config:
    def __init__(self):
        self.parse_args()
    
    def parse_args(self):
        parser = argparse.ArgumentParser(description='DiscoAVR - AV Receiver Web Controller')
        parser.add_argument('--avr-host', default=os.environ.get('AVR_HOST', '192.168.1.100'),
                          help='AV Receiver IP address (default: 192.168.1.100)')
        parser.add_argument('--avr-port', type=int, default=int(os.environ.get('AVR_PORT', 60128)),
                          help='AV Receiver telnet port (default: 60128)')
        parser.add_argument('--avr-timeout', type=int, default=int(os.environ.get('AVR_TIMEOUT', 5)),
                          help='AV Receiver connection timeout (default: 5)')
        parser.add_argument('--host', default=os.environ.get('HOST', 'localhost'),
                          help='Web server host (default: localhost)')
        parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)),
                          help='Web server port (default: 5000)')
        parser.add_argument('--debug', action='store_true',
                          help='Enable debug mode')
        
        self.args = parser.parse_args()
    
    @property
    def AVR_HOST(self):
        return self.args.avr_host
    
    @property
    def AVR_PORT(self):
        return self.args.avr_port
    
    @property
    def AVR_TIMEOUT(self):
        return self.args.avr_timeout
    
    @property
    def HOST(self):
        return self.args.host
    
    @property
    def PORT(self):
        return self.args.port
    
    @property
    def DEBUG(self):
        return self.args.debug