# config.py - 公共配置文件
import pymysql

# MySQL数据库配置
DB_CONFIG = {
    "host": "localhost",    # 主机名
    "user": "work",         # 用户名
    "password": "1111",     # 密码
    "database": "information",  # 数据库名
    "charset": "utf8mb4"
}

# 网络配置
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8888