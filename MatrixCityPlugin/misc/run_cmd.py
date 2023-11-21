import json
import argparse
import subprocess
from pathlib import Path

def main(config_file: str='misc/user.json', background: bool=False):
    config_file = Path(config_file).resolve()
    with open(config_file) as f:
        config: dict = json.load(f)
    ue_command = config['ue_command']
    ue_project = config['ue_project']
    python_script = Path(config['python_script']).resolve()

    if ' ' in ue_project:
        raise ValueError(f"Found blanks in `ue_project` path. UE can't handle that. `ue_project`: {ue_project}")

    py_cmd = [
        f'-ExecutePythonScript="{python_script}"'
    ]
    if background:
        py_cmd = [
            '-run=pythonscript', 
            f'-script="{python_script}"'
        ]

    command = [
        ue_command,
        ue_project,
        'LOG=cmd.log',
    ]
    command.extend(py_cmd)

    ue_log_file = Path(ue_project).parent / "Saved/Logs/cmd.log"
    print(' '.join(map(str, command)) + '\n')

    try:
        subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('Error!')
        print(e)
        print(f'[*] UE log file: {ue_log_file.as_uri()}')
    print('Done!')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='main')
    parser.add_argument('--config_file', '-f', type=str, default='misc/user.json')
    parser.add_argument('--background', '-b', action='store_true')
    args = parser.parse_args()

    main(args.config_file, args.background)
