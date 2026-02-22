"""
AVR Command mappings and UI configuration.
Adjust these for your specific receiver model.
These are common Denon/Marantz commands, modify as needed.
"""
from typing import Dict, List

AVR_COMMANDS: Dict[str, str] = {
    # Presets / Scenes
    'preset_vinyl': 'SIPHONO\nMUOFF\nZ2MUOFF\nMV67\nZ267',

    # Power controls
    'power_on': 'PWON',
    'power_off': 'PWSTANDBY',
    
    # Volume controls
    'volume_up': 'MVUP',
    'volume_down': 'MVDOWN',
    'volume_up_5': 'MVUP\nMVUP\nMVUP\nMVUP\nMVUP',
    'volume_down_5': 'MVDOWN\nMVDOWN\nMVDOWN\nMVDOWN\nMVDOWN',
    'volume_52': 'MV52',
    'volume_56': 'MV56',
    'volume_60': 'MV60',
    'volume_64': 'MV64',
    'volume_68': 'MV68',
    'volume_72': 'MV72',
    'mute_on': 'MUON',
    'mute_off': 'MUOFF',

    # Zone 2 controls
    'zone2_up': 'Z2UP\nZ2UP',
    'zone2_down': 'Z2DOWN\nZ2DOWN',
    'zone2_up_5': 'Z2UP\nZ2UP\nZ2UP\nZ2UP\nZ2UP',
    'zone2_down_5': 'Z2DOWN\nZ2DOWN\nZ2DOWN\nZ2DOWN\nZ2DOWN',
    'zone2_52': 'Z252',
    'zone2_56': 'Z256',
    'zone2_60': 'Z260',
    'zone2_64': 'Z264',
    'zone2_68': 'Z268',
    'zone2_72': 'Z272',
    'zone2_mute_on': 'Z2MUON',
    'zone2_mute_off': 'Z2MUOFF',
    
    # Input sources
    'input_cd': 'SICD',
    'input_dvd': 'SIDVD',
    'input_bluray': 'SIBD',
    'input_tv': 'SITV',
    'input_cable': 'SICBL/SAT',
    'input_aux': 'SIAUX1',
    'input_bluetooth': 'SIBT',
    'input_phono': 'SIPHONO',
    'input_tuner': 'SITUNER',
    
    # Surround modes
    'surround_stereo': 'MSSTEREO',
    'surround_movie': 'MSMOVIE',
    'surround_music': 'MSMUSIC',
    'surround_game': 'MSGAME',
    'surround_auto': 'MSAUTO'
}

# UI groupings for better organization
COMMAND_GROUPS: Dict[str, List[str]] = {
    'presets': ['preset_vinyl'],
    'power': ['power_on', 'power_off'],
    'main_volume': ['volume_up', 'volume_up_5', 'mute_on', 'volume_down', 'volume_down_5', 'mute_off'],
    'main_volume_presets': ['volume_52', 'volume_56', 'volume_60', 'volume_64', 'volume_68', 'volume_72'],
    'zone2_volume': ['zone2_up', 'zone2_up_5', 'zone2_mute_on', 'zone2_down', 'zone2_down_5', 'zone2_mute_off'],
    'zone2_volume_presets': ['zone2_52', 'zone2_56', 'zone2_60', 'zone2_64', 'zone2_68', 'zone2_72'],
    'inputs': ['input_cd', 'input_dvd', 'input_bluray', 'input_tv', 'input_cable', 'input_aux', 'input_bluetooth'],
    'surround': ['surround_stereo', 'surround_movie', 'surround_music', 'surround_auto']
}

# Human-readable labels for UI buttons
COMMAND_LABELS: Dict[str, str] = {
    'preset_vinyl': '🎵 Vinyl',
    'power_on': 'Power On',
    'power_off': 'Power Off',
    'volume_up': 'Vol +',
    'volume_down': 'Vol -',
    'volume_up_5': 'Vol ++',
    'volume_down_5': 'Vol --',
    'volume_52': '52',
    'volume_56': '56',
    'volume_60': '60',
    'volume_64': '64',
    'volume_68': '68',
    'volume_72': '72',
    'mute_on': 'Mute',
    'mute_off': 'Unmute',
    'zone2_up': 'Vol +',
    'zone2_down': 'Vol -',
    'zone2_up_5': 'Vol ++',
    'zone2_down_5': 'Vol --',
    'zone2_52': '52',
    'zone2_56': '56',
    'zone2_60': '60',
    'zone2_64': '64',
    'zone2_68': '68',
    'zone2_72': '72',
    'zone2_mute_on': 'Mute',
    'zone2_mute_off': 'Unmute',
    'input_cd': 'CD',
    'input_dvd': 'DVD',
    'input_bluray': 'Blu-ray',
    'input_tv': 'TV',
    'input_cable': 'Cable/Sat',
    'input_aux': 'AUX',
    'input_bluetooth': 'Bluetooth',
    'surround_stereo': 'Stereo',
    'surround_movie': 'Movie',
    'surround_music': 'Music',
    'surround_auto': 'Auto'
}