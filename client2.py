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
            
            # 第一步：输入外部垃圾图片路径
            print("\n" + "=" * 30)
            print("第一步：外部垃圾图片")
            print("=" * 30)
            
            while True:
                outer_path = input("请输入外部垃圾图片路径（.jpg格式）: ").strip()
                
                # 验证路径格式
                if not outer_path.endswith('.jpg'):
                    print("❌ 图片格式必须是.jpg！")
                    continue
                    
                break  # 格式正确
            
            # 第二步：输入垃圾桶站点编号
            print("\n" + "=" * 30)
            print("第二步：垃圾桶站点编号")
            print("=" * 30)
            
            while True:
                location = input("请输入垃圾桶站点编号（5位字母）: ").strip().upper()
                
                # 验证格式
                if not (len(location) == 5 and location.isalpha()):
                    print("❌ 站点编号必须是5位字母！")
                    continue
                    
                break  # 格式正确
            
            # 连接服务器
            print(f"\n🔗 正在连接服务器 {SERVER_HOST}:{SERVER_PORT}...")
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # 移除超时设置，使用阻塞模式
                # client_socket.settimeout(30)  # 设置为30秒超时
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("✅ 服务器连接成功")
                
                # 第一步：发送外部图片路径和站点编号
                # 格式：外部图片路径|站点编号
                request_data = f"{outer_path}|{location}"
                client_socket.send(request_data.encode("utf-8"))
                print(f"📤 已发送请求：外部图片={outer_path}, 站点={location}")
                
                # 接收服务器返回的垃圾类别
                try:
                    # 设置接收超时
                    client_socket.settimeout(30)  # 设置30秒接收超时
                    cate_str = client_socket.recv(1024).decode("utf-8")  # 垃圾类别
                    print(f"📥 收到垃圾类别：{cate_str}")
                    
                    # 解析类别
                    if cate_str == "5":
                        print("❌ 无法识别：无对应垃圾桶或垃圾类型")
                        print("❌ 操作终止")
                        client_socket.close()
                        continue
                    else:
                        category_names = {
                            "1": "可回收垃圾",
                            "2": "有害垃圾", 
                            "3": "厨余垃圾",
                            "4": "其他垃圾"
                        }
                        cate_name = category_names.get(cate_str, "未知类型")
                        print(f"🗑️  识别结果：{cate_str} ({cate_name})")
                    
                    # 第三步：输入内部垃圾桶图片路径
                    print("\n" + "=" * 30)
                    print("第三步：内部垃圾桶图片")
                    print("=" * 30)
                    print(f"内部图片应命名为：{location}_{cate_str}.jpg")
                    
                    while True:
                        inner_path = input(f"请输入内部垃圾桶图片路径（应为 {location}_{cate_str}.jpg）: ").strip()
                        
                        # 验证路径格式
                        if not inner_path.endswith('.jpg'):
                            print("❌ 图片格式必须是.jpg！")
                            continue
                        
                        # 验证图片名称
                        expected_name = f"{location}_{cate_str}.jpg"
                        actual_name = inner_path.split("/")[-1] if "/" in inner_path else inner_path
                        
                        if actual_name != expected_name:
                            print(f"⚠️  警告：图片名称应为 {expected_name}，但收到的是 {actual_name}")
                            confirm = input("是否继续使用此图片？(y/n): ").strip().lower()
                            if confirm not in ['y', 'yes']:
                                continue
                        
                        break  # 格式正确
                    
                    # 第二步：发送内部图片路径
                    client_socket.send(inner_path.encode("utf-8"))
                    print(f"📤 已发送内部图片：{inner_path}")
                    
                    # 接收服务器返回的存储情况
                    storage_str = client_socket.recv(1024).decode("utf-8")  # 存储百分比
                    
                    print("\n" + "=" * 30)
                    print("服务器最终响应：")
                    print("=" * 30)
                    
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
                    print("❌ 接收响应超时，请检查服务器状态")
                except ConnectionResetError:
                    print("❌ 连接被服务器重置")
                except Exception as e:
                    print(f"❌ 接收响应失败：{e}")
                    
                client_socket.close()
                
            except ConnectionRefusedError:
                print("❌ 无法连接服务器！请检查：")
                print("  1. 服务器是否已启动（运行 server.py）")
                print(f"  2. 服务器地址是否正确：{SERVER_HOST}:{SERVER_PORT}")
            except socket.timeout:
                print("❌ 连接服务器超时")
            except ConnectionResetError:
                print("❌ 连接被拒绝或重置")
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