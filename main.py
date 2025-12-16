import pymysql
import socket
import threading
import time

# MySQL数据库配置（后续可手动修改）
DB_CONFIG = {
    "host": "localhost",    # 主机名占位符
    "user": "work",      # 用户名占位符
    "password": "1111",  # 密码占位符
    "database": "information",     # 数据库名
    "charset": "utf8mb4"
}

# 网络配置
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8888

# -------------------------- 数据库初始化模块 --------------------------
def init_mysql_db():
    """初始化MySQL数据库和表结构（需先手动创建information数据库）"""
    # 1. 连接MySQL（先连接mysql库创建information
    conn_root = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        charset=DB_CONFIG["charset"]
    )
    cursor_root = conn_root.cursor()
    # 创建information数据库（如果不存在）
    cursor_root.execute("CREATE DATABASE IF NOT EXISTS information DEFAULT CHARACTER SET utf8mb4")
    conn_root.close()

    # 2. 连接information数据库，创建表
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 初始化1：创建垃圾桶表（主键：location + category_id）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trash_bin (
        location CHAR(5) NOT NULL,          -- 5位英文字符位置信息
        category_id INT NOT NULL,           -- 垃圾桶类别编号(1-5)
        storage INT DEFAULT 0,              -- 存储情况(0-100)
        PRIMARY KEY (location, category_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')

    # 初始化垃圾桶数据（交互式输入）
    print("\n===== 垃圾桶数据初始化 =====")
    print("输入格式: 位置(5位字母),类别编号(1-5)（例如：ABCDE,3）")
    print("输入 'no' 结束垃圾桶数据初始化")
    while True:
        user_input = input("> 请输入垃圾桶信息: ").strip()
        if user_input.lower() == "no":
            break
        # 解析输入
        parts = user_input.split(",")
        if len(parts) != 2:
            print("格式错误！请重新输入（示例：ABCDE,3）")
            continue
        location, cate_id = parts[0].strip(), parts[1].strip()
        # 验证格式
        if not (len(location) == 5 and location.isalpha()):
            print("位置必须是5位英文字符！")
            continue
        if not cate_id.isdigit() or not (1 <= int(cate_id) <= 5):
            print("类别编号必须是1-5的数字！")
            continue
        # 插入数据（避免重复主键）
        try:
            cursor.execute(
                "INSERT INTO trash_bin (location, category_id) VALUES (%s, %s)",
                (location.upper(), int(cate_id))
            )
            conn.commit()
            print(f"成功添加：位置={location}, 类别={cate_id}")
        except pymysql.IntegrityError:
            conn.rollback()
            print(f"错误：位置{location}+类别{cate_id}已存在！")

    # 初始化2：创建垃圾知识表（主键：name）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trash_knowledge (
        category INT NOT NULL,              -- 垃圾类别(1-4)
        name CHAR(50) NOT NULL,             -- 垃圾名称（主码）
        PRIMARY KEY (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')

    # 初始化垃圾知识数据（交互式输入）
    print("\n===== 垃圾知识数据初始化 =====")
    print("输入格式: 垃圾名称,类别编号(1-4)（例如：矿泉水瓶,1）")
    print("输入 'no' 结束垃圾知识数据初始化")
    while True:
        user_input = input("> 请输入垃圾信息: ").strip()
        if user_input.lower() == "no":
            break
        # 解析输入
        parts = user_input.split(",")
        if len(parts) != 2:
            print("格式错误！请重新输入（示例：矿泉水瓶,1）")
            continue
        name, cate_id = parts[0].strip(), parts[1].strip()
        # 验证格式
        if not name:
            print("垃圾名称不能为空！")
            continue
        if not cate_id.isdigit() or not (1 <= int(cate_id) <= 4):
            print("类别编号必须是1-4的数字！")
            continue
        # 插入数据
        try:
            cursor.execute(
                "INSERT INTO trash_knowledge (name, category) VALUES (%s, %s)",
                (name, int(cate_id))
            )
            conn.commit()
            print(f"成功添加：{name} -> 类别{cate_id}")
        except pymysql.IntegrityError:
            conn.rollback()
            print(f"错误：{name}已存在！")

    # 关闭连接
    cursor.close()
    conn.close()
    print("\n✅ 数据库初始化完成！")

# -------------------------- 服务器端程序 --------------------------
def server_program():
    """服务器端：处理垃圾桶请求，更新/查询MySQL数据库"""
    # 创建TCP服务端
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"\n📡 服务器已启动，监听 {SERVER_HOST}:{SERVER_PORT}")

    def handle_client(client_socket):
        """处理单个客户端连接"""
        # 连接MySQL数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            # 接收客户端发送的图片路径（模拟）
            img_path = client_socket.recv(1024).decode("utf-8").strip()
            print(f"\n📩 收到图像请求：{img_path}")

            # 模拟AI解析过程（人工输入）
            print("\n===== 模拟AI解析 =====")
            trash_name = input("> 请输入AI识别的垃圾名称（如：矿泉水瓶）: ").strip()
            storage = input("> 请输入垃圾桶存储百分比（0-100）: ").strip()
            
            # 验证存储百分比
            while not (storage.isdigit() and 0 <= int(storage) <= 100):
                storage = input("> 格式错误！请输入0-100的数字: ").strip()
            storage = int(storage)

            # 解析图片路径中的垃圾桶位置和类别（假设路径格式：/trash/ABCDE_3.jpg）
            loc_cate = img_path.split("/")[-1].split(".")[0].split("_")
            if len(loc_cate) != 2:
                print("❌ 图片路径格式错误，无法解析垃圾桶位置/类别")
                client_socket.send("5".encode("utf-8"))  # 无对应垃圾桶
                client_socket.send(f"{storage}".encode("utf-8"))
                return
            
            location, cate_id = loc_cate[0], loc_cate[1]
            # 更新数据库存储情况
            cursor.execute(
                "UPDATE trash_bin SET storage = %s WHERE location = %s AND category_id = %s",
                (storage, location, cate_id)
            )
            conn.commit()

            if cursor.rowcount == 0:
                print(f"❌ 无对应垃圾桶：{location}_{cate_id}")
                client_socket.send("5".encode("utf-8"))  # 回复5
            else:
                # 查询垃圾类别编号
                cursor.execute(
                    "SELECT category FROM trash_knowledge WHERE name = %s",
                    (trash_name,)
                )
                result = cursor.fetchone()
                if result:
                    cate_code = str(result[0])
                    print(f"✅ 查询到垃圾类别：{trash_name} -> {cate_code}")
                    client_socket.send(cate_code.encode("utf-8"))  # 回复类别编号
                else:
                    print(f"❌ 无对应垃圾信息：{trash_name}")
                    client_socket.send("5".encode("utf-8"))  # 回复5
            
            # 发送存储情况
            client_socket.send(f"{storage}".encode("utf-8"))
            print(f"✅ 已发送存储情况：{storage}%")

        except Exception as e:
            conn.rollback()
            print(f"❌ 处理请求出错：{e}")
        finally:
            cursor.close()
            conn.close()
            client_socket.close()

    # 循环监听请求
    while True:
        client_socket, addr = server_socket.accept()
        print(f"\n🔌 客户端连接：{addr}")
        # 启动线程处理客户端
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# -------------------------- 垃圾桶客户端程序 --------------------------
def bin_client_program():
    """垃圾桶端：模拟外设交互，与服务器通信"""
    print("\n===== 垃圾桶客户端 =====")
    while True:
        # 模拟检测是否有人放垃圾
        has_garbage = input("\n> 是否有人要放垃圾？(true/false): ").strip().lower()
        while has_garbage not in ["true", "false"]:
            has_garbage = input("> 格式错误！请输入true/false: ").strip().lower()
        
        if has_garbage == "true":
            # 模拟摄像头获取外部垃圾图片路径
            outer_path = input("> 请输入外部垃圾图片路径（例如：/trash/ABCDE_3.jpg）: ").strip()
            # 模拟摄像头获取内部垃圾图片路径（固定字符串示例）
            inner_path = input("> 请输入内部垃圾图片路径（直接回车使用默认）: ").strip()
            if not inner_path:
                inner_path = "/trash/internal_default.jpg"
            
            # 连接服务器
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                # 发送外部图片路径（核心请求）
                client_socket.send(outer_path.encode("utf-8"))
                
                # 接收服务器回复
                cate_str = client_socket.recv(1024).decode("utf-8")  # 字符串1：垃圾类别/5
                storage_str = client_socket.recv(1024).decode("utf-8")  # 字符串2：存储百分比
                
                # 输出结果
                print(f"\n📢 垃圾类别编号：{cate_str}")
                print(f"📊 垃圾桶存储情况：{storage_str}%")
                
                # 判断是否触发警报
                if int(storage_str) > 80:
                    print("⚠️  警报：垃圾桶存储量超过80%！")
                
                client_socket.close()
            except ConnectionRefusedError:
                print("❌ 无法连接服务器，请先启动服务器！")
            except Exception as e:
                print(f"❌ 客户端出错：{e}")
        else:
            print("⏳ 等待有人放垃圾...")
            time.sleep(1)

# -------------------------- 主程序入口 --------------------------
if __name__ == "__main__":
    # 第一步：初始化MySQL数据库
    try:
        init_mysql_db()
    except pymysql.Error as e:
        print(f"❌ 数据库连接失败：{e}")
        print("请检查MySQL配置（主机/用户名/密码），确保MySQL服务已启动！")
        exit(1)
    
    # 第二步：启动服务器（后台线程）
    threading.Thread(target=server_program, daemon=True).start()
    time.sleep(1)  # 等待服务器启动
    
    # 第三步：启动垃圾桶客户端
    bin_client_program()
