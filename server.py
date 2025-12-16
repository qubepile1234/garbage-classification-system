# server.py - 服务器端程序
import socket
import threading
import pymysql
from config import DB_CONFIG, SERVER_HOST, SERVER_PORT

def handle_client(client_socket, addr):
    """处理单个客户端连接"""
    print(f"\n🔌 客户端连接：{addr}")
    
    # 连接MySQL数据库
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except pymysql.Error as e:
        print(f"❌ 数据库连接失败：{e}")
        client_socket.send("数据库连接失败".encode("utf-8"))
        client_socket.close()
        return

    try:
        # 接收客户端发送的图片路径
        img_path = client_socket.recv(1024).decode("utf-8").strip()
        print(f"📩 收到图像请求：{img_path}")

        # 解析图片路径中的垃圾桶位置和类别
        try:
            filename = img_path.split("/")[-1]
            basename = filename.split(".")[0]
            location, cate_id = basename.split("_")
            
            if len(location) != 5 or not location.isalpha():
                raise ValueError("位置格式错误")
            if not cate_id.isdigit():
                raise ValueError("类别ID格式错误")
                
            print(f"📦 解析结果：位置={location}, 类别ID={cate_id}")
            
        except (IndexError, ValueError) as e:
            print(f"❌ 图片路径格式错误：{e}")
            print("  预期格式：/trash/ABCDE_3.jpg")
            client_socket.send("5".encode("utf-8"))  # 无对应垃圾桶
            client_socket.send("0".encode("utf-8"))  # 默认存储
            return

        # 模拟AI解析过程（人工输入）
        print("\n" + "=" * 30)
        print("AI垃圾识别模拟")
        print("=" * 30)
        
        while True:
            trash_name = input("> 请输入识别的垃圾名称（如：矿泉水瓶）: ").strip()
            if trash_name:
                break
            print("❌ 垃圾名称不能为空！")
        
        while True:
            storage = input("> 请输入垃圾桶存储百分比（0-100）: ").strip()
            if storage.isdigit() and 0 <= int(storage) <= 100:
                storage = int(storage)
                break
            print("❌ 请输入0-100的数字！")

        # 更新数据库存储情况
        try:
            cursor.execute(
                "UPDATE trash_bin SET storage = %s WHERE location = %s AND category_id = %s",
                (storage, location.upper(), cate_id)
            )
            conn.commit()
            
            if cursor.rowcount == 0:
                print(f"❌ 未找到垃圾桶：{location}_{cate_id}")
                # 检查该垃圾桶是否存在
                cursor.execute(
                    "SELECT 1 FROM trash_bin WHERE location = %s AND category_id = %s",
                    (location.upper(), cate_id)
                )
                if not cursor.fetchone():
                    print(f"  提示：请先在数据库中创建该垃圾桶")
                client_socket.send("5".encode("utf-8"))  # 回复5
            else:
                print(f"✅ 已更新垃圾桶 {location}_{cate_id} 存储为 {storage}%")
                
                # 查询垃圾类别编号
                cursor.execute(
                    "SELECT category FROM trash_knowledge WHERE name = %s",
                    (trash_name,)
                )
                result = cursor.fetchone()
                
                if result:
                    cate_code = str(result[0])
                    print(f"✅ 查询结果：{trash_name} -> 类别{cate_code}")
                    client_socket.send(cate_code.encode("utf-8"))  # 回复类别编号
                else:
                    print(f"❌ 未找到垃圾信息：{trash_name}")
                    print(f"  提示：请先在数据库中添加该垃圾")
                    client_socket.send("5".encode("utf-8"))  # 回复5
                
        except pymysql.Error as e:
            conn.rollback()
            print(f"❌ 数据库操作失败：{e}")

        # 发送存储情况
        client_socket.send(f"{storage}".encode("utf-8"))
        print(f"📤 已发送存储情况：{storage}%")

    except ConnectionResetError:
        print(f"❌ 客户端 {addr} 连接断开")
    except Exception as e:
        print(f"❌ 处理请求时出错：{e}")
    finally:
        cursor.close()
        conn.close()
        client_socket.close()
        print(f"🔌 客户端 {addr} 连接关闭")

def server_program():
    """服务器主程序"""
    print("=" * 50)
    print("智能垃圾桶服务器")
    print("=" * 50)
    print(f"监听地址：{SERVER_HOST}:{SERVER_PORT}")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)

    # 创建TCP服务端
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        print(f"✅ 服务器已启动，等待客户端连接...")
        
        while True:
            client_socket, addr = server_socket.accept()
            # 启动新线程处理客户端
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, addr),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n\n🛑 正在关闭服务器...")
    except Exception as e:
        print(f"❌ 服务器启动失败：{e}")
    finally:
        server_socket.close()
        print("✅ 服务器已关闭")

if __name__ == "__main__":
    server_program()