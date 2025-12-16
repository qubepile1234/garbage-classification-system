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
        # 第一步：接收客户端发送的外部图片路径和站点编号
        # 格式：外部图片路径|站点编号
        request_data = client_socket.recv(1024).decode("utf-8").strip()
        print(f"📩 收到请求：{request_data}")
        
        # 解析请求数据
        if "|" not in request_data:
            print("❌ 请求格式错误，应为：外部图片路径|站点编号")
            client_socket.send("5".encode("utf-8"))  # 发送错误代码
            return
        
        outer_path, location = request_data.split("|", 1)
        print(f"📦 解析结果：外部图片={outer_path}, 站点={location}")
        
        # 验证站点编号格式
        if not (len(location) == 5 and location.isalpha()):
            print(f"❌ 站点编号格式错误：{location}")
            client_socket.send("5".encode("utf-8"))  # 发送错误代码
            return
        
        # 验证外部图片格式
        if not outer_path.endswith('.jpg'):
            print(f"❌ 外部图片格式错误：{outer_path}")
            client_socket.send("5".encode("utf-8"))  # 发送错误代码
            return
        
        # 模拟AI解析外部垃圾图片（人工输入）
        print("\n" + "=" * 30)
        print("第一步：AI垃圾识别模拟")
        print("=" * 30)
        
        while True:
            trash_name = input("> 请输入识别的垃圾名称（如：矿泉水瓶）: ").strip()
            if trash_name:
                break
            print("❌ 垃圾名称不能为空！")
        
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
            return
        
        # 第二步：接收内部垃圾桶图片路径
        inner_path = client_socket.recv(1024).decode("utf-8").strip()
        print(f"📩 收到内部图片：{inner_path}")
        
        # 验证内部图片格式
        if not inner_path.endswith('.jpg'):
            print(f"❌ 内部图片格式错误：{inner_path}")
            client_socket.send("0".encode("utf-8"))  # 发送默认存储
            return
        
        # 解析内部图片名称，获取垃圾桶类别
        try:
            filename = inner_path.split("/")[-1] if "/" in inner_path else inner_path
            basename = filename.split(".")[0]
            
            # 期望格式：位置_类别
            if "_" not in basename:
                raise ValueError("内部图片名称格式错误")
                
            inner_location, inner_cate_id = basename.split("_", 1)
            
            # 验证内部图片中的位置是否与外部一致
            if inner_location != location:
                print(f"⚠️  警告：内部图片位置({inner_location})与外部位置({location})不一致")
            
            # 验证类别是否匹配
            if inner_cate_id != cate_code:
                print(f"⚠️  警告：内部图片类别({inner_cate_id})与识别类别({cate_code})不一致")
                
            # 这里不验证类别范围，因为内部图片可能对应1-5的任何类别
                
        except Exception as e:
            print(f"⚠️  内部图片名称解析警告：{e}")
            # 继续处理，不中断
        
        # 模拟AI解析内部图片（人工输入存储情况）
        print("\n" + "=" * 30)
        print("第二步：垃圾桶存储情况分析")
        print("=" * 30)
        print(f"当前处理的垃圾桶：位置={location}, 类别={cate_code}")
        
        # 先查询当前存储情况
        cursor.execute(
            "SELECT storage FROM trash_bin WHERE location = %s AND category_id = %s",
            (location.upper(), cate_code)
        )
        current_storage_result = cursor.fetchone()
        
        if current_storage_result:
            current_storage = current_storage_result[0]
            print(f"当前存储情况：{current_storage}%")
        else:
            print("⚠️  警告：数据库中不存在该垃圾桶")
            print(f"  位置={location}, 类别={cate_code}")
            current_storage = 0
        
        # 人工输入存储情况
        while True:
            storage_input = input(f"> 请输入更新后的存储百分比（0-100，当前：{current_storage}%）: ").strip()
            if storage_input.isdigit() and 0 <= int(storage_input) <= 100:
                new_storage = int(storage_input)
                break
            print("❌ 请输入0-100的数字！")
        
        # 更新数据库存储情况
        try:
            cursor.execute(
                "UPDATE trash_bin SET storage = %s WHERE location = %s AND category_id = %s",
                (new_storage, location.upper(), cate_code)
            )
            conn.commit()
            
            if cursor.rowcount == 0:
                print(f"❌ 未找到垃圾桶：{location}_{cate_code}")
                print("  注意：数据库更新失败，但继续发送存储情况给客户端")
            else:
                print(f"✅ 已更新垃圾桶 {location}_{cate_code} 存储为 {new_storage}%")
                
        except pymysql.Error as e:
            conn.rollback()
            print(f"❌ 数据库更新失败：{e}")
            print("  注意：数据库更新失败，但继续发送存储情况给客户端")
        
        # 发送存储情况给客户端
        client_socket.send(f"{new_storage}".encode("utf-8"))
        print(f"📤 已发送存储情况：{new_storage}%")

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