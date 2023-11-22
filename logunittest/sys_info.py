import datetime, os, sys
import platform
import socket
import subprocess
import psutil
import yaml
from dataclasses import dataclass, asdict


@dataclass
class Data:
    python_executable: str
    python_version: str
    hostname: str
    operating_system: str
    os_version: str
    os_latest_update: str  # Placeholder for latest OS update
    os_architecture: str
    timestamp: str
    cpu: dict
    memory: dict
    in_docker: bool
    docker_build_time: str
    latest_commit_id: str

    def __post_init__(self):
        self.to_yaml()

    def to_yaml(self):
        yaml_str = yaml.dump(asdict(self), default_flow_style=False)
        self.yaml_data = yaml_str  # Save the YAML string as an attribute

    def __str__(self):
        return yaml.dump(asdict(self), default_flow_style=False)


# Usage in your existing SysInfo class remains the same


class SysInfo:
    def __init__(self, *args, pgDir=None, **kwargs):
        self.pgDir = pgDir if pgDir is not None else os.getcwd()
        self.get_data(*args, **kwargs)

    def get_data(self, *args, pgName=None, **kwargs):
        self.data = Data(
            python_executable=f"{sys.executable.replace(self.pgDir, f'{pgName}')}",
            python_version=sys.version,
            hostname=socket.gethostname(),
            operating_system=platform.system(),
            os_version=platform.version(),
            os_latest_update="N/A",  # To be implemented based on specific OS
            os_architecture=platform.machine(),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cpu=self.get_cpu_info(),
            memory=self.get_memory_info(),
            in_docker=self.running_in_docker(),
            latest_commit_id=self.get_latest_merge_commit_id(),
            docker_build_time="N/A",  # Placeholder, requires Docker-specific implementation
        )

    def get_cpu_info(self):
        return {
            "Processor": platform.processor(),
            "Physical Cores": psutil.cpu_count(logical=False),
            "Total Cores": psutil.cpu_count(logical=True),
        }

    def get_memory_info(self):
        virtual_memory = psutil.virtual_memory()
        return {"Total Memory": virtual_memory.total, "Available Memory": virtual_memory.available}

    def get_latest_merge_commit_id(self):
        try:
            # Git command to get the most recent merge commit
            return subprocess.run(
                ["git", "log", "-n", "1", "--format=format:%H"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            # Handle cases where Git command fails (e.g., no merge commits, Git not installed, etc.)
            return "Not available"

    def running_in_docker(self):
        return os.path.exists("/.dockerenv")


if __name__ == "__main__":
    # Example usage
    sys_info = SysInfo()
    print(sys_info.data.yaml_data)
