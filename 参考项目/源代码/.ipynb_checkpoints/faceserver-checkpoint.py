import socket
import time

# 创建套接字并监听
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 6666))
server_socket.listen(1)

print("等待客户端连接...")
client, addr = server_socket.accept()
print(f"客户端 {addr} 已连接")

# 接收图片数据
print("开始接收图片数据...")
image_data = b''
while True:
    data = client.recv(1024)
    if not data:
        break
    image_data += data

# 保存图片数据到文件
image_filename = f"received_image_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
with open(image_filename, "wb") as f:
    f.write(image_data)
print(f"图片 {image_filename} 保存完成")

# 关闭连接
client.close()
server_socket.close()