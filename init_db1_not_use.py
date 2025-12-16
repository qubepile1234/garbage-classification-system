# init_db.py - 数据库初始化程序
import pymysql
from config import DB_CONFIG

def init_mysql_db():
    """初始化MySQL数据库和表结构"""
    print("=" * 50)
    print("数据库初始化工具")
    print("=" * 50)
    
    # 1. 连接MySQL（先连接mysql库创建information数据库）
    try:
        conn_root = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            charset=DB_CONFIG["charset"]
        )
        cursor_root = conn_root.cursor()
        print("✅ 已连接到MySQL服务器")
        
        # 创建information数据库（如果不存在）
        cursor_root.execute("CREATE DATABASE IF NOT EXISTS information DEFAULT CHARACTER SET utf8mb4")
        print("✅ 数据库 'information' 已准备就绪")
        conn_root.close()
    except pymysql.Error as e:
        print(f"❌ MySQL连接失败：{e}")
        print("请检查：")
        print("1. MySQL服务是否已启动")
        print("2. config.py中的配置是否正确")
        print("3. 用户名/密码是否正确")
        return False

    # 2. 连接information数据库，创建表
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 已连接到 'information' 数据库")
    except pymysql.Error as e:
        print(f"❌ 连接information数据库失败：{e}")
        return False

    # 初始化1：创建垃圾桶表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trash_bin (
        location CHAR(5) NOT NULL,          -- 5位英文字符位置信息
        category_id INT NOT NULL,           -- 垃圾桶类别编号(1-5)
        storage INT DEFAULT 0,              -- 存储情况(0-100)
        PRIMARY KEY (location, category_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    print("✅ 垃圾桶表 'trash_bin' 已创建")

    # 初始化垃圾桶数据（交互式输入）
    print("\n" + "=" * 30)
    print("垃圾桶数据初始化")
    print("=" * 30)
    print("输入格式: 位置(5位字母),类别编号(1-5)")
    print("示例: ABCDE,3")
    print("输入 'no' 结束，输入 'list' 查看已添加的数据")
    
    bin_count = 0
    while True:
        user_input = input("\n> 请输入垃圾桶信息: ").strip()
        
        if user_input.lower() == 'no':
            break
            
        if user_input.lower() == 'list':
            cursor.execute("SELECT location, category_id FROM trash_bin")
            bins = cursor.fetchall()
            if bins:
                print("当前已添加的垃圾桶:")
                for loc, cate in bins:
                    print(f"  位置: {loc}, 类别: {cate}")
            else:
                print("尚未添加任何垃圾桶")
            continue
        
        # 解析输入
        parts = user_input.split(",")
        if len(parts) != 2:
            print("❌ 格式错误！请重新输入（示例：ABCDE,3）")
            continue
            
        location, cate_id = parts[0].strip(), parts[1].strip()
        
        # 验证格式
        if not (len(location) == 5 and location.isalpha()):
            print("❌ 位置必须是5位英文字符！")
            continue
            
        if not cate_id.isdigit() or not (1 <= int(cate_id) <= 5):
            print("❌ 类别编号必须是1-5的数字！")
            continue
            
        # 插入数据
        try:
            cursor.execute(
                "INSERT INTO trash_bin (location, category_id) VALUES (%s, %s)",
                (location.upper(), int(cate_id))
            )
            conn.commit()
            bin_count += 1
            print(f"✅ 成功添加：位置={location.upper()}, 类别={cate_id}")
        except pymysql.IntegrityError:
            conn.rollback()
            print(f"❌ 该垃圾桶已存在！位置{location.upper()}+类别{cate_id}")

    # 初始化2：创建垃圾知识表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trash_knowledge (
        category INT NOT NULL,              -- 垃圾类别(1-4)
        name CHAR(50) NOT NULL,             -- 垃圾名称（主码）
        PRIMARY KEY (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    ''')
    print("\n✅ 垃圾知识表 'trash_knowledge' 已创建")

    # 初始化垃圾知识数据（交互式输入）
    print("\n" + "=" * 30)
    print("垃圾知识数据初始化")
    print("=" * 30)
    print("输入格式: 垃圾名称,类别编号(1-4)")
    print("示例: 矿泉水瓶,1")
    print("垃圾类别说明：")
    print("  1-可回收垃圾  2-有害垃圾  3-厨余垃圾  4-其他垃圾")
    print("输入 'no' 结束，输入 'list' 查看已添加的数据")
    
    knowledge_count = 0
    while True:
        user_input = input("\n> 请输入垃圾信息: ").strip()
        
        if user_input.lower() == 'no':
            break
            
        if user_input.lower() == 'list':
            cursor.execute("SELECT name, category FROM trash_knowledge")
            items = cursor.fetchall()
            if items:
                print("当前已添加的垃圾知识:")
                for name, cate in items:
                    print(f"  {name} -> 类别{cate}")
            else:
                print("尚未添加任何垃圾知识")
            continue
        
        # 解析输入
        parts = user_input.split(",")
        if len(parts) != 2:
            print("❌ 格式错误！请重新输入（示例：矿泉水瓶,1）")
            continue
            
        name, cate_id = parts[0].strip(), parts[1].strip()
        
        # 验证格式
        if not name:
            print("❌ 垃圾名称不能为空！")
            continue
            
        if not cate_id.isdigit() or not (1 <= int(cate_id) <= 4):
            print("❌ 类别编号必须是1-4的数字！")
            continue
            
        # 插入数据
        try:
            cursor.execute(
                "INSERT INTO trash_knowledge (name, category) VALUES (%s, %s)",
                (name, int(cate_id))
            )
            conn.commit()
            knowledge_count += 1
            print(f"✅ 成功添加：{name} -> 类别{cate_id}")
        except pymysql.IntegrityError:
            conn.rollback()
            print(f"❌ 该垃圾名称已存在！")

    # 关闭连接
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ 数据库初始化完成！")
    print(f"   - 添加垃圾桶: {bin_count} 个")
    print(f"   - 添加垃圾知识: {knowledge_count} 条")
    print("=" * 50)
    return True

if __name__ == "__main__":
    init_mysql_db()
    input("\n按 Enter 键退出...")