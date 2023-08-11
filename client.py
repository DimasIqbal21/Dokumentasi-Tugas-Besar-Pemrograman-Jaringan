import socket
import threading
import os


class Client():
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Replace with the IP address of the server machine
        self.server_address = ('10.217.17.83', 2323)
        self.client_socket.connect(self.server_address)
        self.username = input("Masukkan nama Anda: ")
        self.client_socket.send(bytes(self.username, encoding='utf-8'))

        self.receive_thread = threading.Thread(target=self.receive_message)
        self.send_thread = threading.Thread(target=self.send_message)
        self.receive_thread.start()
        self.send_thread.start()

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("file:"):
                    self.receive_file(message[5:])
                else:
                    print(message)
            except Exception as e:
                print(f"Terjadi kesalahan pada koneksi dengan server: {e}")
                self.client_socket.close()
                break

    def receive_file(self, file_info):
        try:
            file_size, file_name, relative_folder, sender_username = file_info.split(
                ':', 3)
            file_size = int(file_size)

            file_path = os.path.join(relative_folder, file_name)
            with open(file_path, 'wb') as file:
                remaining_bytes = file_size
                while remaining_bytes > 0:
                    data = self.client_socket.recv(1024)
                    file.write(data)
                    remaining_bytes -= len(data)

            print(
                f"File '{file_name}' berhasil diterima dari {sender_username}.")
        except Exception as e:
            print(f"Terjadi kesalahan saat menerima file: {e}")

    def send_message(self):
        while True:
            try:
                message = input()
                if message == "file":
                    self.send_file()
                else:
                    self.client_socket.send(bytes(message, encoding='utf-8'))
            except Exception as e:
                print(f"Terjadi kesalahan saat mengirim pesan: {e}")
                self.client_socket.close()
                break

    def send_file(self):
        try:
            recipient = input("Masukkan nama penerima file: ")
            file_path = input("Masukkan path file yang akan dikirim: ")
            if not os.path.exists(file_path):
                print("File tidak ditemukan.")
                return

            with open(file_path, 'rb') as file:
                file_data = file.read()

            file_info = f"{len(file_data)}:{os.path.basename(file_path)}:./:{recipient}"
            self.client_socket.send(
                bytes(f"file:{file_info}", encoding='utf-8'))
            self.client_socket.sendall(file_data)
            print("File berhasil dikirim.")
        except Exception as e:
            print(f"Terjadi kesalahan saat mengirim file: {e}")


if __name__ == "__main__":
    print("Tutorial :")
    print("1. mengirimkan secara unicast ketikan @'username_tujuan':'pesan' ")
    print("2. mengirimkan file ketikan file enter, masukan username tujuan, masukan path file ")
    print("3. jika mengetika pesan langsung maka akan mengirimkan secara multicast ke semua user/clien yang terhubung")
    Client()
