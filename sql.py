import os
import mysql.connector
from mysql.connector import Error
from PIL import Image
import datetime

def create_database_and_table():
    """创建数据库和表"""
    try:
        # 连接到MySQL服务器（请修改为你的MySQL连接信息）
        connection = mysql.connector.connect(
            host='localhost',
            user='work',           # 你的MySQL用户名
            password='1111' # 你的MySQL密码
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS image_database")
            print("数据库创建成功或已存在")
            
            # 切换到新数据库
            cursor.execute("USE image_database")
            
            # 创建表
            create_table_query = """
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT,
                image_width INT,
                image_height INT,
                file_format VARCHAR(50),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_file (file_path)
            )
            """
            cursor.execute(create_table_query)
            print("数据表创建成功或已存在")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"数据库创建错误: {e}")
        return False

def get_image_info(image_path):
    """获取图片的详细信息"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_format = img.format
        return width, height, file_format
    except Exception as e:
        print(f"无法读取图片信息 {image_path}: {e}")
        return None, None, None

def store_images_to_database(folder_path):
    """将文件夹中的JPG图片信息存储到数据库"""
    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host='localhost',
            user='work',
            password='1111',
            database='image_database'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 统计变量
            total_files = 0
            successful_files = 0
            
            # 遍历文件夹中的所有文件
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    total_files += 1
                    file_path = os.path.join(folder_path, filename)
                    
                    try:
                        # 获取文件信息
                        file_size = os.path.getsize(file_path)
                        image_width, image_height, file_format = get_image_info(file_path)
                        
                        # 插入数据到数据库
                        insert_query = """
                        INSERT INTO images (file_name, file_path, file_size, image_width, image_height, file_format)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            file_size = VALUES(file_size),
                            image_width = VALUES(image_width),
                            image_height = VALUES(image_height),
                            file_format = VALUES(file_format)
                        """
                        
                        cursor.execute(insert_query, (
                            filename,
                            file_path,
                            file_size,
                            image_width,
                            image_height,
                            file_format
                        ))
                        
                        successful_files += 1
                        print(f"成功处理: {filename}")
                        
                    except Exception as e:
                        print(f"处理文件 {filename} 时出错: {e}")
                        continue
            
            # 提交事务
            connection.commit()
            print(f"\n处理完成! 总共找到 {total_files} 个JPG文件，成功存储 {successful_files} 个")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"数据库连接错误: {e}")

def display_stored_images():
    """显示数据库中存储的图片信息"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='work',
            password='1111',
            database='image_database'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM images")
            total_count = cursor.fetchone()[0]
            
            print(f"\n数据库中总共存储了 {total_count} 张图片")
            print("\n最近添加的10张图片:")
            print("-" * 100)
            
            cursor.execute("""
                SELECT id, file_name, file_size, image_width, image_height, created_time 
                FROM images 
                ORDER BY created_time DESC 
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            for row in results:
                file_size_kb = row[2] / 1024 if row[2] else 0
                print(f"ID: {row[0]}, 文件名: {row[1]}, 大小: {file_size_kb:.1f}KB, "
                      f"尺寸: {row[3]}x{row[4]}, 添加时间: {row[5]}")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"查询数据库错误: {e}")

def main():
    """主函数"""
    print("=== JPG图片信息存储到MySQL数据库 ===")
    
    # 第一步：创建数据库和表
    print("\n1. 正在创建数据库和表...")
    if not create_database_and_table():
        print("数据库创建失败，程序退出")
        return
    
    # 第二步：获取用户输入的文件夹路径
    print("\n2. 请输入包含JPG图片的文件夹路径:")
    folder_path = input("文件夹路径: ").strip()
    
    # 移除路径两端的引号（如果用户复制路径时带了引号）
    folder_path = folder_path.strip('"\'')
    
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 路径 '{folder_path}' 不存在")
        return
    
    if not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}' 不是一个文件夹")
        return
    
    # 第三步：处理图片并存储到数据库
    print(f"\n3. 正在处理文件夹: {folder_path}")
    store_images_to_database(folder_path)
    
    # 第四步：显示存储结果
    display_stored_images()
    
    print("\n程序执行完成!")

if __name__ == "__main__":
    main()