import socket
import os

def send_data():
    # 配置服务器信息（填服务器端的 IP 和端口）
    HOST = '192.168.3.10'  # 必须与服务器端 IP 一致
    PORT = 8888

    # 创建 TCP 套接字并连接
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("成功连接服务器！")
        except ConnectionRefusedError:
            print("连接失败，请检查服务器是否启动或 IP/端口是否正确！")
            return

        while True:
            # 选择发送类型
            choice = input("\n请选择发送类型：1-字符串 2-图片 3-退出\n输入编号：")
            if choice == '3':
                print("断开连接...")
                break

            # 发送字符串
            elif choice == '1':
                content = input("请输入要发送的字符串：")
                # 发送类型标识符 + 字符串长度（4字节） + 字符串内容
                s.sendall(b'STR' + len(content).to_bytes(4, byteorder='big') + content.encode('utf-8'))
                print("字符串发送成功！")

            # 发送图片
            elif choice == '2':
                img_path = input("请输入图片文件路径（例：C:/test.jpg 或 ./img.png）：")
                if not os.path.exists(img_path):
                    print("文件不存在，请重新输入！")
                    continue
                # 获取图片大小
                img_size = os.path.getsize(img_path)
                # 发送类型标识符 + 图片大小（8字节） + 图片数据
                s.sendall(b'IMG' + img_size.to_bytes(8, byteorder='big'))
                with open(img_path, 'rb') as f:
                    while chunk := f.read(4096):
                        s.sendall(chunk)
                print("图片发送成功！")

            else:
                print("输入错误，请重新选择！")

if __name__ == "__main__":
    send_data()
