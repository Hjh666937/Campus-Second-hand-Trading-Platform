"""一键初始化数据库：建库建表（schema.sql）+ 写入演示数据（seed.py）。

用法：
    cd backend
    python db/setup_db.py

可重复执行：已存在的库、表和数据会自动跳过。
"""

import os
import re
import sys

import pyodbc
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GO_PATTERN = re.compile(r"^\s*GO\s*$", re.IGNORECASE | re.MULTILINE)


def split_batches(script):
    """按 GO 把 T-SQL 脚本拆成可逐条执行的批次。"""
    return [batch.strip() for batch in GO_PATTERN.split(script) if batch.strip()]


def main():
    server = os.getenv("DB_SERVER", "127.0.0.1,1433")
    user = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD", "")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={user};PWD={password};"
        "TrustServerCertificate=yes;Encrypt=yes"
    )

    schema_path = os.path.join(BASE_DIR, "db", "schema.sql")
    with open(schema_path, encoding="utf-8-sig") as file:
        batches = split_batches(file.read())

    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        for batch in batches:
            cursor.execute(batch)

    print(f"建库建表完成，共执行 {len(batches)} 个批次。")

    sys.path.insert(0, BASE_DIR)
    import seed

    seed.main()


if __name__ == "__main__":
    main()
