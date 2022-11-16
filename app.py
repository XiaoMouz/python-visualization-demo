from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

hostname = ''  # 数据库ip，本机即为 localhost 或 127.0.0.1
port = ''  # 数据库端口，默认 3306
database = ''  # 数据库名称
username = ''  # 数据库用户名通常为 root
password = ''  # 数据库密码
db_uri = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 远端数据库 job 表 ORM 模型
class Job(db.Model):
    __tablename__ = 'job'
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


@app.route('/')
def index():
    # index 没有看的必要，直接重定向即可
    return redirect('/area')


@app.route('/area')
def area():
    # 得到所有数据
    data = Job.query.all()

    # 思路：题目要求是每个区域的薪资分布图，也就是所有区域因此不对数据地区进行筛选
    # 前端的箱线图要求使用数组形式的数据，并且是成队的数组与 key 对应
    # 因此先地区对应的 value 应使用列表，value 中存入所有的工资数据（不是总工资，是遇到对应的就向列表中添加数值
    areaData = {i.Palce: [] for i in data}

    # 列表使用 append 方法加入新值
    for i in data:
        areaData[i.Palce].append(getSalary(i.Salary))

    # 为了方便前端读取进行数据分离然后返回
    return render_template("areaEffSalary-boxplot.html", place=list(areaData.keys()), salary=list(areaData.values()))


@app.route('/work-bar')
def work():
    # contains 模糊查询, 使用 like 会只返回上海
    data = Job.query.filter(Job.JobName.contains('大数据'), Job.Palce.contains('上海'))

    # 思路： 题目要求是地区与工作数量的关系
    # key 为地区 value 则是对应有多少工作
    # 直接在遇到对应的地区时将 value + 1 即可
    place = {i.Palce: 0 for i in data}
    # 在找到对应的 key 后更新 value 值
    for i in data:
        n = place.get(i.Palce)
        place[i.Palce] = n + 1

    # 为了方便前端读取进行数据分离然后返回
    return render_template("bigData-work-bar-map.html", workPlaceData=list(place.keys()),
                           workNumbersData=list(place.values()))


@app.route('/request-Edu')
def edu():
    data = Job.query.filter(Job.JobName.contains('大数据'))

    # 思路： 题目要求是学历与工作数量的关系
    # key 为学历 value 则是对应有多少工作
    # 直接在遇到对应的学历时将 value + 1 即可
    eduData = {i.Education: 0 for i in data}
    for i in data:
        n = eduData.get(i.Education)
        eduData[i.Education] = n + 1
    # 由于 pie 图的数据要求，不做分类处理，直接回传让 jinja 做善后
    return render_template("requestEdu-pie-map.html", data=eduData)


@app.route('/work-Time')
def workTime():
    data = Job.query.filter(Job.JobName.contains('大数据'))

    # 思路： 与 workType (即岗位类型所影响薪资)的思路相同
    # 由于需要计算平均值，因此需要为对应工龄计算总共录入多少数据
    # 因此规划两个字典 key 都是工龄
    # timeData 的 value 用于计算录入的数据数量
    # salaryData 的 value 用于计算工资总量
    timeData = {getWorkAge(i.WorkAge): 0 for i in data}
    salaryData = {getWorkAge(i.WorkAge): 0 for i in data}
    # 数据导入
    for i in data:
        # 计算数据数量
        time = timeData.get(getWorkAge(i.WorkAge))
        time = time + 1
        timeData[getWorkAge(i.WorkAge)] = time

        # 计算总量工资
        salary = salaryData.get(getWorkAge(i.WorkAge))
        salary = salary + getSalary(i.Salary)
        salaryData[getWorkAge(i.WorkAge)] = salary

    # 计算平均数
    for key, value in salaryData.items():
        time = timeData.get(key)
        salary = salaryData.get(key)
        salary = salary / time  # 因为前面使用了相同的 key 所以能够直接读取计算平均值
        salaryData[key] = int(salary)  # 重新赋值给 salaryData 的 value

    # 为了方便前端读取进行数据分离然后返回
    return render_template("workTime4salary-line-map.html", workAge=list(salaryData.keys()),
                           salaryData=list(salaryData.values()))


@app.route('/work-Type')
def workType():
    data = Job.query.filter(Job.JobName.contains('大数据'))

    # 思路： 与 workTime (即工龄影响薪资的可视化数据)的思路相同
    # 由于需要计算平均值，因此需要为对应地区计算总共录入多少数据
    # 因此规划两个字典 key 都是工作标签
    # timeData 的 value 用于计算录入的数据数量
    # salaryData 的 value 用于计算工资总量
    timeData = {i.WorkKind: 0 for i in data}
    salaryData = {i.WorkKind: 0 for i in data}

    # 数据赋值
    for i in data:
        # 计算数据数量
        time = timeData.get(i.WorkKind)
        time = time + 1
        timeData[i.WorkKind] = time

        # 计算总工资
        salary = salaryData.get(i.WorkKind)
        salary = salary + getSalary(i.Salary)
        salaryData[i.WorkKind] = salary

    # 计算工资平均数
    for key, value in salaryData.items():
        time = timeData.get(key)
        salary = salaryData.get(key)
        salary = salary / time  # 因为前面使用了相同的 key 所以能够直接读取计算平均值
        salaryData[key] = int(salary)  # 重新赋值给 salaryData 的 value
    # 为了方便前端读取进行数据分离然后返回
    return render_template("workType-AvgSalary-line-map.html", workType=list(salaryData.keys()),
                           salaryData=list(salaryData.values()))


# 由于远端数据是字符因此需要一个方法来分割字符串取得数据
# 本方法用于解决 Salary 的字符分割问题，返回值取平均数
# 传入: 1 万元/月  24 万元/年   300元/天
# 返回: 10000     20000       9000
def getSalary(salary):
    if salary[-1] == '月':
        # print(salary) #debug
        try:
            salaryMin = salary.split('-')[0]
            salaryMax = salary.split('-')[1][0:-3]
            if salary[-3] == '万':
                # print(f"min:{min},max:{max}") # debug
                salaryMin = float(salaryMin) * 10000
                salaryMax = float(salaryMax) * 10000
            elif salary[-3] == '千':
                salaryMin = float(salaryMin) * 1000
                salaryMax = float(salaryMax) * 1000
            return int((salaryMax + salaryMin) / 2)
        except:
            salary = salary[0:-3]
            salary = float(salary) * 10000
            return int(salary)
    elif salary[-1] == '年':
        try:
            salaryMin = salary.split('-')[0]
            salaryMax = salary.split('-')[1][0:-3]
            # print(f"min:{min},max:{max}") # debug
            if salary[-3] == '万':
                salaryMin = float(salaryMin) * 10000
                salaryMax = float(salaryMax) * 10000
            return int(((salaryMax + salaryMin) / 2) / 12)
        except:
            salary = salary[0:-3]
            salary = float(salary) * 10000
            return int(salary / 12)
    elif salary[-1] == '天':
        try:
            salaryMin = salary.split('-')[0]
            salaryMax = salary.split('-')[1][0:-3]
            # print(f"min:{min},max:{max}") #debug
            if salary[-3] == '元':
                salaryMin = float(salaryMin)
                salaryMax = float(salaryMax)
            return int((salaryMax + salaryMin) * 30 / 2)
        except:
            salary = salary[0:-3]
            salary = float(salary)
            return int(salary * 30)
    else:
        return 0


# 由于远端数据是字符因此需要一个方法来分割字符串取得数据
# 本方法用于解决 Salary 的字符分割问题，返回值取最小值
# 传入: 无需经验  在校生/应届生  5年工龄
# 返回: 0        0           5
def getWorkAge(workyear):
    if workyear == '无需经验' or workyear == '在校生/应届生':
        return 0
    else:
        try:
            min = workyear.split('-')[0]
            max = workyear.split('-')[1][0:-3]  # 我爱异常: 在无法切割时直接抛出处理嘻嘻
            return int(min)
        except:
            try:
                return int(workyear.split('年')[0])
            except:
                return 0


if __name__ == "__main__":
    app.run(port=5500, debug=True)
