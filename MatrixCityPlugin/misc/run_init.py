import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT = 'misc'
PLUGIN_NAME = 'XRFeitoriaGear'

# from data.config import CfgNode

def mklink(project_dir: Path, name: str):
    plugin_dir = project_dir / name / PLUGIN_NAME
    plugin_dir.parent.mkdir(exist_ok=True)

    # check if the plugin is already linked
    if plugin_dir.exists() or plugin_dir.is_symlink():
        is_delete = input(f'Found existing plugin dir: {plugin_dir}\n'
                            'Delete it? (Y/n): ')
        if is_delete == '' or is_delete.lower() == 'y':
            if plugin_dir.is_symlink():
                plugin_dir.unlink()
            else:
                shutil.rmtree(plugin_dir)
        else:
            return

    mklink = [
        "cmd", "/c", "mklink", '/d',
        str(plugin_dir),
        str(Path.cwd())
    ]
    subprocess.check_call(mklink)


def main(config_file=f'{ROOT}/user.json'):
    with open(config_file) as f:
        config = json.load(f)
    ue_command = Path(config['ue_command'])
    ue_project_file = Path(config['ue_project'])
    ue_project_dir = ue_project_file.parent

    if ' ' in str(ue_project_file):
        raise ValueError(f"Found blanks in `ue_project` path. UE can't handle that. `ue_project`: {ue_project_file}")
    
    ue_python = ue_command.parents[1] / 'ThirdParty/Python3/Win64/python.exe'
    req_file = Path.cwd() / ROOT / 'requirements.txt'
    req_ue_file = Path.cwd() / ROOT / 'requirements_ue.txt'

    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # pip install for ue python
    subprocess.check_call([
        str(ue_python), 
        '-m', 'pip', 'install', 
        '--no-warn-script-location', 
        '-r', str(req_ue_file),
    ])

    # pip install for the current python
    subprocess.check_call([
        sys.executable, 
        "-m", "pip", "install", 
        '--no-warn-script-location', 
        '-r', str(req_file),
    ])

    print('\n-------pip install done.--------')

    try:
        mklink(ue_project_dir, 'Plugins')
    except subprocess.CalledProcessError:
        print('Failed to create symbolic link. Please run this script as administrator.')
    

    print('\n-------mklink install done.--------')

    print('\n-------Initialization done.--------')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-f', type=str, default='misc/user.json')
    args = parser.parse_args()

    main(args.config_file)