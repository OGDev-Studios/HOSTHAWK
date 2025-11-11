import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from dataclasses import dataclass, field, asdict


@dataclass
class ScannerConfig:
    timeout: float = 2.0
    threads: int = 50
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: int = 100
    log_level: str = "INFO"
    log_file: Optional[str] = "hosthawk.log"
    log_dir: str = "logs"
    output_dir: str = "output"
    reports_dir: str = "reports"
    max_scan_duration: int = 3600
    enable_os_detection: bool = True
    enable_service_detection: bool = True
    enable_vulnerability_scan: bool = False
    user_agent: str = "HostHawk/1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ScannerConfig':
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ScannerConfig':
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def save_to_file(self, config_path: str) -> None:
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class WebConfig:
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: Optional[str] = None
    max_content_length: int = 16777216
    session_timeout: int = 3600
    cors_enabled: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])
    
    def __post_init__(self):
        if self.secret_key is None:
            self.secret_key = os.urandom(24).hex()


def load_config(config_path: Optional[str] = None) -> ScannerConfig:
    if config_path and os.path.exists(config_path):
        return ScannerConfig.from_file(config_path)
    
    env_config = {
        'timeout': float(os.getenv('HOSTHAWK_TIMEOUT', '2.0')),
        'threads': int(os.getenv('HOSTHAWK_THREADS', '50')),
        'log_level': os.getenv('HOSTHAWK_LOG_LEVEL', 'INFO'),
        'log_file': os.getenv('HOSTHAWK_LOG_FILE', 'hosthawk.log'),
        'output_dir': os.getenv('HOSTHAWK_OUTPUT_DIR', 'output'),
        'reports_dir': os.getenv('HOSTHAWK_REPORTS_DIR', 'reports'),
    }
    
    return ScannerConfig(**env_config)


def get_default_config_path() -> Path:
    return Path.home() / '.hosthawk' / 'config.json'
