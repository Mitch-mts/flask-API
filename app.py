from flask import Flask, render_template

from ServiceFunctions import ServiceFunctions

app = Flask(__name__)

# dataset paths
studentDataSetPath = "./data/StudentPerformance.csv"
athletesDataSetPath = "./data/Athletes.xlsx"

functions = ServiceFunctions()

"""
start of python flask functions
"""


# function to extract dataset values and setting a specific required row count
def getStudentDataSet():
    try:
        data = functions.getCsvDataSetInfoForFirstTenRecords(studentDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {studentDataSetPath}, Reason: {e}</p>"


def getAthletesInfoFromTheHead():
    try:
        data = functions.getExcelDataSetInfoForFirstTenRecords(athletesDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

    # get dataset info from tail


def getAthletesInfoFromTheTail():
    try:
        data = functions.getExcelDataSetInfoForLastTenRecords(athletesDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

    # get dataset shape

"""
end of python flask functions
"""

print("data set shape ", functions.getDataSetShape())
print("data set unique values ", functions.combineDataSetColumns())


#### start of python flask APIs ####

# defines a route that maps the root url of the app to helloWorld function
@app.route('/')
def helloWorld():  # function defines logic for handling requests to root url
    return "Hello, from your flask app!"


@app.route('/studentsInfo')
def studentInformation():
    data = getStudentDataSet()
    return render_template("studentInfo.html", table_data=data)


@app.route('/athletesInfoHead')
def athletesInformationHead():
    data = getAthletesInfoFromTheHead()
    return render_template("athletesInfo.html", table_data=data)


@app.route('/athletesInfoTail')
def athletesInformationTail():
    data = getAthletesInfoFromTheTail()
    return render_template("athletesInfo.html", table_data=data)


@app.route('/hello')
def hello():
    functions.hello_world()


#### end of python flask APIs ####
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
