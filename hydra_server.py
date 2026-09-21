"""
Launches a TCP server that can be used to run Hydra from a different program
on the same machine.

If you need help using this, write an issue on GitHub or message me on Discord
so I can place higher priority on instructions / polish.
"""
import socket
import select

import hydra.hyutil as hyutil

HOST = 'localhost'
PORT = 4477

c_sock = None


def str_to_protocol(msg):
    msg_bytes = msg.encode('utf-8')
    msg_len = len(msg_bytes).to_bytes(4, byteorder='little', signed=False)
    return msg_len + msg_bytes

def _send_message(msg):
    c_sock.sendall(str_to_protocol(msg))
    
def handle_message(c_sock, msg):
    raise Exception("Deprecated")
    print(f"\tReceived message: {msg}")
    
    tokens = msg.split('|')
    match tokens[0]:
        case 'scansongs':
            print(f"Function: scan songs with list {tokens[1:]}")
            _procedure_scan()
            # Procedure:
            # server sends back "scan_started", then begins scanning
            #   will respond to "cancelscan" but nothing else
            # UI receives "scan_started"
            #   will switch to scan progress UI and listen for updates
            #   UX can send "cancelscan"
            #   UX can timeout or react to disconnection
            # server sends "scan_discovery_progress"
            # sever sends "scan_discovery_complete"
            # server sends "scan_work_progress"
            # server sends "scan_work_complete"
            #   UI and server return to normal state
        case _:
            print(f"\tUnknown message code.")
            send_reply(c_sock, "error|Unknown code was ignored.")


def _receive_message(c_sock):
    msg_len = None
    data_buffer = bytearray()
    while True:
        # Read a chunk of data.
        try:
            data_in = c_sock.recv(1024)
            if data_in == b'':
                print("Connection was closed.")
                return
            data_buffer += data_in
        except ConnectionResetError as e:
            print(f"Connection reset: {e}")
            return

        # (No message length yet) Check if buffer is long enough to read message length
        if msg_len is None and len(data_buffer) >= 4:
            msg_len = int.from_bytes(data_buffer[:4], byteorder='little', signed=False)
            data_buffer = data_buffer[4:]
        
        # (Has message length) Check if buffer is long enough to read the next message
        if msg_len is not None and len(data_buffer) >= msg_len:
            return data_buffer[:msg_len].decode('utf-8')

def _cb_scan(progress_count):
    _send_message(f"scan_step1_progress|{progress_count}")

def _cb_scan2(progress_count):
    _send_message(f"scan_step2_progress|{progress_count}")

def _handle_single_connection(server_sock):
    global c_sock
    # Block until connection.
    print("Waiting for connection...")
    c_sock, address = server_sock.accept()

    with c_sock:
        print(f"Connected to {address}.")
        
        # Idle - We expect a command for the first message.
        cmd_msg = _receive_message(c_sock)
        print(f"Received command message: {cmd_msg}")
        
        tokens = cmd_msg.split('|')
        cmd, cmdargs = tokens[0], tokens[1:]
        match cmd:
            case 'scansongs':
                # Step 1: Scan for chart locations & get total song count.
                print(f"Function: scan songs with list {tokens[1:]}")
                chart_calls, errors = hyutil.scan_discover_step(cmdargs, cb_progress=_cb_scan)
                print(f"Done. Errors: {errors}")
                
                # Step 2: Get metadata and add to db
                print(f"DB step:")
                success_count, errors2 = hyutil.scan_db_step(chart_calls, cb_progress=_cb_scan2)
                print(f"Done.")
                
                # Send result keys and values
                _send_message(f"kv|success_count|{success_count}")
                for err in errors + errors2:
                    _send_message(f"kv|errorstr|{err}")
            case _:
                print(f"\tUnknown message code.")
        
        # Kinda optional if "100% progress" is sent but let's be nice
        _send_message(f"end")
        
        # Just waiting so that client can end on their terms
        _receive_message(c_sock)
    
    print("End of connection.")

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((HOST, PORT))
        server_sock.listen()

        while True:
            _handle_single_connection(server_sock)
