import ast
import asyncio
import datetime
import time
import json
import socket
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Optional

import colorama
import psutil
import win32gui
import win32process

from config import CfgNode

p = None
output_path = None
unreal_loaded = False


def setup_logging(log_path: Path):
    logging.basicConfig(
        level=logging.INFO, 
        format='[%(asctime)s] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_path)),
            logging.StreamHandler()
        ]
    )

    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level=logging.DEBUG)
    ch.setFormatter(formatter)

    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("asyncio").addHandler(ch)

    logging.info(f'Python Logging to {log_path.as_uri()}')


def format_time(seconds: float) -> str:
    return time.strftime("%Hh %Mm %Ss", time.gmtime(seconds))


def calculate_remaining_time(i_current, n_total, time_log: List[float]) -> str:
    remaining_time = 'N/A'
    if len(time_log) > 0:
        avg_time = sum(time_log) / len(time_log)
        remaining_time = (n_total - i_current) * avg_time
        remaining_time = format_time(remaining_time)
    return remaining_time


def ask_exit():
    for task in asyncio.all_tasks():
        task.cancel()


async def handle_client(client, host='127.0.0.1', port=9999, parent_loop=None):
    global unreal_loaded
    loop__ = asyncio.get_event_loop()
    while True:
        try:
            data_size = await loop__.sock_recv(client, 4)  # 4 byte (int32) size prefix on the message (ue defined)
            data_size = int.from_bytes(data_size, byteorder='little')
            data = (await loop__.sock_recv(client, data_size)).decode()
        except OSError:
            if parent_loop:
                # logging.info('Error Occurred. Restarting Unreal Engine & Socket Connection...\n')
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind((host, port))
                server.listen(8)
                server.setblocking(False)
                client, _ = await parent_loop.sock_accept(server)
                logging.info(f'Socket Connection from {client.getpeername()}')

        if not data:
            break
            
        logging.info(data)

        if data == '[*] Unreal Engine Loaded!':
            unreal_loaded = True

        # handle error
        if 'error' in data.lower():
            if p:
                logging.error('Unreal Engine Exit with Error. Killing Unreal Engine...')
                p.kill()
        
        # handle exit
        if data == 'Render completed. Success: True' or data == 'Pipeline Finished' or 'exit' in data.lower():
            if p:
                logging.info('Exiting Unreal Engine...')
                p.kill()
            break

        # await loop.sock_sendall(client, data.encode('utf8'))
    client.close()
    ask_exit()


async def run_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(8)
    server.setblocking(False)

    loop_ = asyncio.get_event_loop()

    # while True:
    client, _ = await loop_.sock_accept(server)
    logging.info(f'Socket Connection from {client.getpeername()}')
    loop_.create_task(handle_client(client, host, port, loop_))


def get_window_title_and_pid() -> dict:
    def callback(hwnd, hwnds):
        # if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
        hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    titles = {}
    for hwnd in hwnds:
        title = win32gui.GetWindowText(hwnd)
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        titles[title] = found_pid
    return titles


async def run_cmd(command):
    global p, unreal_loaded
    unreal_loaded = False
    p = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    logging.info('[*] Starting Unreal Engine...')
    logging.info(f'[*] Unreal Engine PID: {p.pid}')

    crash_titles = ['crash', 'error', 'message']

    if sys.version_info[1] > 8:
        AsyncioCancelledError = asyncio.exceptions.CancelledError
    else:
        AsyncioCancelledError = asyncio.CancelledError

    while True:
        try:
            await asyncio.sleep(10)
            poll = p.poll()

            windows_titles = get_window_title_and_pid()
            ue_titles = []
            for title, pid in windows_titles.items():
                # ue crash reporter (not in same pid)
                if 'crash' in title.lower():
                    p_ = psutil.Process(pid)
                    p_.kill()
                # ue window titles
                if p.pid == pid:
                    ue_titles.append(title)

            ue_titles = ', '.join(ue_titles).lower()
            crashed = [title in ue_titles for title in crash_titles]
            if poll or any(crashed) or (ue_titles == '' and unreal_loaded):
                p.kill()
                logging.error(f'[!] Unreal Engine crashed with poll code {poll}, windows titles: {ue_titles}')
                logging.info('------------------')
                logging.info('[*] Restarting Unreal Engine...')
                logging.info(f'[*] Unreal Engine PID: {p.pid}')
                unreal_loaded = False
                p = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except AsyncioCancelledError as e:
            break
            # continue
        # logging.info('running', poll)


def main(config_file: str='misc/user.json'):
    colorama.init(autoreset=True)

    config_file = Path(config_file).resolve()
    with open(config_file) as f:
        config = json.load(f)
    ue_command = config['ue_command']
    ue_project = config['ue_project']

    global output_path
    render_config_path = Path(config['render_config']).resolve()
    render_config = CfgNode.load_yaml_with_base(str(render_config_path))
    output_path = Path(render_config['Output_Path']).resolve()
    python_log_file = output_path / f'_config/log_{datetime.datetime.now().strftime("%m-%d_%H-%M-%S")}.log'
    python_log_file.parent.mkdir(parents=True, exist_ok=True)
    setup_logging(python_log_file)

    if ' ' in ue_project:
        raise ValueError(f"Found blanks in `ue_project` path. UE can't handle that. `ue_project`: {ue_project}")

    # python_dir = Path(ue_project).parent / 'Plugins/XRFeitoriaGear/Content/Python'
    # python_script = python_dir / 'pipeline.py'
    python_script = Path(config['python_script']).resolve()

    command = [
        f'"{ue_command}"',
        f'"{ue_project}"',
        # f'-run=pythonscript -script="{python_script}"',
        # f'-ExecutePythonScript="{python_script}"',
        f'-ExecCmds="py {python_script}"',
        f'-render_config_path={render_config_path}',
        f'-notexturestreaming',
        f'-silent',
        f'LOG=Pipeline.log',
        f'-LOCALLOGTIMES',
    ]
    command = ' '.join(map(str, command))
    logging.info(colorama.Fore.BLUE + command)

    ue_log_file = Path(ue_project).parent / "Saved/Logs/Pipeline.log"
    logging.info(colorama.Fore.YELLOW + f'[*] UE log file: {ue_log_file.as_uri()}')

    host = '127.0.0.1'
    port = 9999

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(run_server(host, port))
        loop.run_until_complete(run_cmd(command))

        # asyncio.ensure_future(run_server(host, port)),
        # asyncio.ensure_future(run_cmd(command))
        # loop.run_forever()

    except KeyboardInterrupt:
        global p
        if p:
            p.kill()
            logging.info('[*] Unreal Engine is killed by keyboard interrupt.')
        pass

    else:
        # logging.info("Pipeline Finished!")
        loop.close()
        logging.info(f'output_path: {output_path.as_uri()}')


        # TODO: add post-processing
        # logging.info('Doing some post-processing...')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='main')
    parser.add_argument('--config_file', '-f', type=str, default='misc/user.json')
    args = parser.parse_args()

    main(args.config_file)
