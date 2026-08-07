"""
Launches a TCP server that can be used to run Hydra from a different program
on the same machine.

If you need help using this, write an issue on GitHub or message me on Discord
so I can place higher priority on instructions / polish.
"""
import socket

HOST = 'localhost'
PORT = 4477

def str_to_protocol(msg):
    msg_bytes = msg.encode('utf-8')
    msg_len = len(msg_bytes).to_bytes(4, byteorder='little', signed=False)
    return msg_len + msg_bytes

def send_reply(c_sock, reply):
    c_sock.sendall(str_to_protocol(reply))
    print(f"\t\tSent reply message: {reply}")
    
def handle_message(c_sock, msg):
    print(f"\tReceived message: {msg}")
    reply = None
    try:
        code = int(msg[:3])
        tail = msg[3:]
    except ValueError as e:
        print(f"\tNon-coded message.")
        send_reply(c_sock, "Non-coded message was ignored.")
        return
    
    match code:
        case 100:
            pass
        case _:
            print(f"\tUnknown message code.")
            send_reply(c_sock, "Unknown code was ignored.")
        


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((HOST, PORT))
        server_sock.listen()

        # Wait for connection.
        print("Waiting for connection...")
        c_sock, address = server_sock.accept()

        with c_sock:
            print(f"Connected to {address}.")
            
            data_buffer = bytearray()
            msg_len = None
            
            while True:
                # Read a chunk of data.
                try:
                    data_in = c_sock.recv(1024)
                    if data_in == b'':
                        print("Connection was closed.")
                        break
                    data_buffer += data_in
                except ConnectionResetError as e:
                    print(f"Connection reset: {e}")
                    break
            
                # (No message length yet) Check if buffer is long enough to read message length
                if msg_len is None and len(data_buffer) >= 4:
                    msg_len = int.from_bytes(data_buffer[:4], byteorder='little', signed=False)
                    data_buffer = data_buffer[4:]
                
                # (Has message length) Check if buffer is long enough to read the next message
                if msg_len is not None and len(data_buffer) >= msg_len:
                    msg = data_buffer[:msg_len].decode('utf-8')
                    data_buffer = data_buffer[msg_len:]
                    msg_len = None
                    
                    # Handle message
                    try:
                        handle_message(c_sock, msg)
                    except ConnectionResetError as e:
                        print(f"Connection reset: {e}")
                        break

            
            print("End of connection.")