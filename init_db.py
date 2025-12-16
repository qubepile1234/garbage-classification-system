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

    # 初始化垃圾桶数据（简化输入）
    print("\n" + "=" * 30)
    print("垃圾桶数据初始化")
    print("=" * 30)
    print("说明：输入一个5位字母的位置，将自动创建5个垃圾桶（类别1-5）")
    print("示例：输入 ABCDE")
    print("将自动创建：ABCDE_1, ABCDE_2, ABCDE_3, ABCDE_4, ABCDE_5")
    print("输入 'no' 结束，输入 'list' 查看已添加的数据")
    print("输入 'clear' 清空所有垃圾桶数据")
    
    bin_count = 0
    while True:
        user_input = input("\n> 请输入垃圾桶位置 (5位字母): ").strip().upper()
        
        if user_input.lower() == 'no':
            break
            
        if user_input.lower() == 'list':
            cursor.execute("SELECT location, category_id, storage FROM trash_bin ORDER BY location, category_id")
            bins = cursor.fetchall()
            if bins:
                print("\n当前已添加的垃圾桶:")
                print("-" * 40)
                current_loc = None
                for loc, cate, storage in bins:
                    if loc != current_loc:
                        print(f"\n位置: {loc}")
                        current_loc = loc
                    print(f"  类别 {cate}: 存储量 {storage}%")
            else:
                print("尚未添加任何垃圾桶")
            continue
            
        if user_input.lower() == 'clear':
            confirm = input("⚠️  确定要清空所有垃圾桶数据吗？(yes/no): ").strip().lower()
            if confirm == 'yes':
                cursor.execute("DELETE FROM trash_bin")
                conn.commit()
                print("✅ 已清空所有垃圾桶数据")
                bin_count = 0
            continue
        
        # 验证输入格式
        if not (len(user_input) == 5 and user_input.isalpha()):
            print("❌ 位置必须是5位英文字符！")
            continue
        
        # 自动为该位置创建5个垃圾桶（类别1-5）
        location = user_input.upper()
        added_count = 0
        existed_count = 0
        
        for cate_id in range(1, 6):  # 类别1到5
            try:
                cursor.execute(
                    "INSERT INTO trash_bin (location, category_id) VALUES (%s, %s)",
                    (location, cate_id)
                )
                added_count += 1
                print(f"✅ 已添加：位置={location}, 类别={cate_id}")
            except pymysql.IntegrityError:
                conn.rollback()
                existed_count += 1
                # 检查是否已存在，如果存在则跳过
                cursor.execute(
                    "SELECT 1 FROM trash_bin WHERE location = %s AND category_id = %s",
                    (location, cate_id)
                )
                if cursor.fetchone():
                    print(f"⚠️  已存在：位置={location}, 类别={cate_id}")
        
        conn.commit()
        bin_count += added_count
        
        if added_count > 0:
            print(f"\n✅ 成功为位置 {location} 创建了 {added_count} 个垃圾桶")
        if existed_count > 0:
            print(f"⚠️  {existed_count} 个垃圾桶已存在，未重复创建")

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
    print("输入 'clear' 清空所有垃圾知识数据")
    print("输入 'batch' 批量导入预设垃圾数据")
    
    knowledge_count = 0
    # 预设的常见垃圾数据
    preset_trash_data = {
        "可回收垃圾": [
            "矿泉水瓶", "易拉罐", "报纸", "书本", "纸箱",
            "玻璃瓶", "塑料瓶", "金属罐", "废旧衣物", "纸盒"
        ],
        "有害垃圾": [
            "废电池", "过期药品", "废灯管", "废油漆桶",
            "杀虫剂瓶", "废温度计", "废血压计", "废胶片"
        ],
        "厨余垃圾": [
            "剩饭剩菜", "果皮", "菜叶", "蛋壳", "骨头",
            "茶叶渣", "过期食品", "咖啡渣", "花卉"
        ],
        "其他垃圾": [
            "卫生纸", "塑料袋", "陶瓷碎片", "烟头",
            "一次性餐具", "尘土", "废旧纸巾", "尿不湿"
        ]
    }
    
    while True:
        user_input = input("\n> 请输入垃圾信息: ").strip()
        
        if user_input.lower() == 'no':
            break
            
        if user_input.lower() == 'list':
            cursor.execute("SELECT name, category FROM trash_knowledge ORDER BY category, name")
            items = cursor.fetchall()
            if items:
                print("\n当前已添加的垃圾知识:")
                print("-" * 40)
                current_cate = None
                for name, cate in items:
                    if cate != current_cate:
                        category_names = {1: "可回收垃圾", 2: "有害垃圾", 3: "厨余垃圾", 4: "其他垃圾"}
                        print(f"\n{category_names.get(cate, '未知')} (类别{cate}):")
                        current_cate = cate
                    print(f"  {name}")
            else:
                print("尚未添加任何垃圾知识")
            continue
            
        if user_input.lower() == 'clear':
            confirm = input("⚠️  确定要清空所有垃圾知识数据吗？(yes/no): ").strip().lower()
            if confirm == 'yes':
                cursor.execute("DELETE FROM trash_knowledge")
                conn.commit()
                print("✅ 已清空所有垃圾知识数据")
                knowledge_count = 0
            continue
            
        if user_input.lower() == 'batch':
            print("\n开始批量导入预设垃圾数据...")
            batch_count = 0
            for category_num, (category_name, trash_list) in enumerate(preset_trash_data.items(), 1):
                for trash_name in trash_list:
                    try:
                        cursor.execute(
                            "INSERT INTO trash_knowledge (name, category) VALUES (%s, %s)",
                            (trash_name, category_num)
                        )
                        batch_count += 1
                        print(f"✅ 导入: {trash_name} -> {category_name}")
                    except pymysql.IntegrityError:
                        conn.rollback()
                        # 已存在，跳过
                        pass
            
            conn.commit()
            knowledge_count += batch_count
            print(f"\n✅ 批量导入完成！共添加 {batch_count} 条垃圾知识")
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
            category_names = {1: "可回收垃圾", 2: "有害垃圾", 3: "厨余垃圾", 4: "其他垃圾"}
            cate_name = category_names.get(int(cate_id), "未知")
            print(f"✅ 成功添加：{name} -> {cate_name}(类别{cate_id})")
        except pymysql.IntegrityError:
            conn.rollback()
            print(f"❌ 该垃圾名称已存在！")

    # 统计最终数据
    cursor.execute("SELECT COUNT(*) FROM trash_bin")
    total_bins = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trash_knowledge")
    total_knowledge = cursor.fetchone()[0]

    # 关闭连接
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ 数据库初始化完成！")
    print(f"   - 垃圾桶总数: {total_bins} 个")
    print(f"   - 垃圾知识总数: {total_knowledge} 条")
    print("\n使用说明:")
    print("1. 启动服务器: python server.py")
    print("2. 启动客户端: python client.py")
    print("3. 在客户端中，使用路径格式: /trash/位置_类别.jpg")
    print("   例如: /trash/ABCDE_3.jpg")
    print("=" * 50)
    return True

if __name__ == "__main__":
    init_mysql_db()
    input("\n按 Enter 键退出...")