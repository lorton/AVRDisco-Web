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
    'volume_40': 'MV40',
    'volume_55': 'MV55',
    'volume_70': 'MV70',
    'mute_on': 'MUON',
    'mute_off': 'MUOFF',
    
    # Zone 2 controls
    'zone2_up': 'Z2UP\nZ2UP',
    'zone2_down': 'Z2DOWN\nZ2DOWN',
    'zone2_up_5': 'Z2UP\nZ2UP\nZ2UP\nZ2UP\nZ2UP',
    'zone2_down_5': 'Z2DOWN\nZ2DOWN\nZ2DOWN\nZ2DOWN\nZ2DOWN',
    'zone2_40': 'Z240',
    'zone2_55': 'Z255',
    'zone2_70': 'Z270',
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
    'main_volume_presets': ['volume_40', 'volume_55', 'volume_70'],
    'zone2_volume': ['zone2_up', 'zone2_up_5', 'zone2_mute_on', 'zone2_down', 'zone2_down_5', 'zone2_mute_off'],
    'zone2_volume_presets': ['zone2_40', 'zone2_55', 'zone2_70'],
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
    'volume_40': 'Vol 40',
    'volume_55': 'Vol 55',
    'volume_70': 'Vol 70',
    'mute_on': 'Mute',
    'mute_off': 'Unmute',
    'zone2_up': 'Vol +',
    'zone2_down': 'Vol -',
    'zone2_up_5': 'Vol ++',
    'zone2_down_5': 'Vol --',
    'zone2_40': 'Vol 40',
    'zone2_55': 'Vol 55',
    'zone2_70': 'Vol 70',
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