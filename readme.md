# Question Project

一个 `flask` 与 `echart JS` 搭配题目的解决方案
本 repo 用于未来可能需要的复习与检索，如有帮助给个 `::star star` 即可

### 目的

该解决方案旨在测试 `flask`,`SQLAlchemy`,`jinja` 与 `echart JS` 的基本使用，无重难点

测试了 `flask` 与 `jinja` 的配合使用来让 `echart JS` 生成符合预期的可视化图表，并且还测试了通过 `SQLAlchemy` 来读取远端数据库中表的数据，生成相应的 ORM 模型以供处理与返回给前端

### 环境要求

> python >= 3.10.6

拉取本 repo 后在文件夹中打开终端输入:
```bash
pip install -r requirements.txt
```

repo 中的  *job.csv* 即为数据，可以转成 xlsx 文件格式后通过 navicat 等数据库管理软件导入数据库即可

修改 `app.py` 中关于数据库连接的字段:

```python
hostname = ''  # 数据库ip，本机即为 localhost 或 127.0.0.1
port = ''  # 数据库端口，默认 3306
database = ''  # 数据库名称
username = ''  # 数据库用户名通常为 root
password = ''  # 数据库密码
db_uri = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

以及在 `job` 类中的 `__tablename__` 字段:

```python
class Job(db.Model):
    __tablename__ = ''  # 输入你将 job.csv 导入到的表的表名
    id = db.Column(db.Integer, primary_key=True, nullable=True, autoincrement=True)
    JobName = db.Column(db.VARCHAR(100))
    WorkUrl = db.Column(db.Text)
    CompanyName = db.Column(db.VARCHAR(100))
    Salary = db.Column(db.VARCHAR(100))
    Education = db.Column(db.VARCHAR(100))
    WorkAge = db.Column(db.VARCHAR(100))
    Palce = db.Column(db.VARCHAR(100))
    CompanyKind = db.Column(db.VARCHAR(100))
    CompanyNumber = db.Column(db.VARCHAR(100))
    WorkTag = db.Column(db.VARCHAR(100))
    NeedWorkNumber = db.Column(db.VARCHAR(100))
    WorkKind = db.Column(db.VARCHAR(100))
    WorkPlace = db.Column(db.VARCHAR(100))
```
