# client.py - 垃圾桶客户端程序
import socket
import time
from config import SERVER_HOST, SERVER_PORT

def bin_client_program():
    """垃圾桶客户端主程序"""
    print("=" * 50)
    print("智能垃圾桶客户端")
    print("=" * 50)
    print("模拟垃圾桶与服务器的交互")
    print("按 Ctrl+C 退出程序")
    print("-" * 50)
    
    while True:
        try:
            # 模拟检测是否有人放垃圾
            print("\n" + "-" * 30)
            has_garbage = input("是否有人要放垃圾？(y/n): ").strip().lower()
            
            if has_garbage not in ['y', 'yes', 'n', 'no']:
                print("❌ 请输入 y/n 或 yes/no")
                continue
                
            if has_garbage in ['n', 'no']:
                print("⏳ 等待中...")
                time.sleep(2)
                continue
            
            # 输入外部垃圾图片路径
            print("\n图片路径格式：/trash/位置_类别.jpg")
            print("示例：/trash/ABCDE_3.jpg")
            print("位置：5位大写字母")
            print("类别：1-5（垃圾桶类型）")
            
            while True:
                outer_path = input("请输入外部垃圾图片路径: ").strip()
                
                # 验证路径格式
                if not outer_path.endswith('.jpg'):
                    print("❌ 路径应以.jpg结尾")
                    continue
                    
                try:
                    # 尝试解析路径
                    filename = outer_path.split("/")[-1]
                    basename = filename.split(".")[0]
                    parts = basename.split("_")
                    
                    if len(parts) != 2:
                        print("❌ 路径格式错误，应为：/trash/位置_类别.jpg")
                        continue
                        
                    location, cate_id = parts
                    
                    if len(location) != 5 or not location.isalpha():
                        print("❌ 位置必须是5位字母")
                        continue
                        
                    if not cate_id.isdigit() or not (1 <= int(cate_id) <= 5):
                        print("❌ 类别必须是1-5的数字")
                        continue
                        
                    break  # 格式正确
                        
                except Exception as e:
                    print(f"❌ 路径解析错误：{e}")
                    continue
            
            # 连接服务器
            print(f"\n🔗 正在连接服务器 {SERVER_HOST}:{SERVER_PORT}...")
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(10)  # 设置10秒超时
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("✅ 服务器连接成功")
                
                # 发送外部图片路径
                client_socket.send(outer_path.encode("utf-8"))
                print(f"📤 已发送请求：{outer_path}")
                
                # 接收服务器回复
                try:
                    cate_str = client_socket.recv(1024).decode("utf-8")  # 垃圾类别
                    storage_str = client_socket.recv(1024).decode("utf-8")  # 存储百分比
                    
                    print("\n" + "=" * 30)
                    print("服务器响应结果：")
                    print("=" * 30)
                    
                    # 解析类别
                    if cate_str == "5":
                        print("❌ 无法识别：无对应垃圾桶或垃圾类型")
                    else:
                        category_names = {
                            "1": "可回收垃圾",
                            "2": "有害垃圾", 
                            "3": "厨余垃圾",
                            "4": "其他垃圾"
                        }
                        cate_name = category_names.get(cate_str, "未知类型")
                        print(f"🗑️  垃圾类别：{cate_str} ({cate_name})")
                    
                    # 显示存储情况
                    try:
                        storage = int(storage_str)
                        print(f"📊 存储情况：{storage}%")
                        
                        # 显示存储状态
                        if storage == 0:
                            print("🟢 状态：空")
                        elif storage <= 50:
                            print("🟡 状态：正常")
                        elif storage <= 80:
                            print("🟠 状态：较满")
                        elif storage <= 95:
                            print("🔴 状态：满")
                            print("⚠️  警报：请及时清理！")
                        else:
                            print("🔴 状态：已满")
                            print("🚨 紧急警报：垃圾桶已满，请立即清理！")
                            
                    except ValueError:
                        print(f"📊 存储情况：{storage_str}% (解析错误)")
                        
                except socket.timeout:
                    print("❌ 接收响应超时")
                except Exception as e:
                    print(f"❌ 接收响应失败：{e}")
                    
                client_socket.close()
                
            except ConnectionRefusedError:
                print("❌ 无法连接服务器！请检查：")
                print("  1. 服务器是否已启动（运行 server.py）")
                print(f"  2. 服务器地址是否正确：{SERVER_HOST}:{SERVER_PORT}")
            except socket.timeout:
                print("❌ 连接服务器超时")
            except Exception as e:
                print(f"❌ 连接失败：{e}")
                
        except KeyboardInterrupt:
            print("\n\n🛑 正在退出客户端...")
            break
        except Exception as e:
            print(f"❌ 程序出错：{e}")
            continue
    
    print("✅ 客户端已关闭")

if __name__ == "__main__":
    bin_client_program()