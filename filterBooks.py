
from flask import Flask,request,jsonify,render_template,url_for
app = Flask(__name__)
import psycopg2
import os
hostame="ec2-54-211-210-149.compute-1.amazonaws.com"
username="asoknnbmofmyeg"
password="d143a33e1b0561a1acfce811161e5216ce2cf33b3a6fbd07f43b19e33f1ffd2d"
database="dj6iu7914th7h"

conn = psycopg2.connect(dbname=database,user=username,password=password,hostame=hostame)

@app.route('/')
def hello_world():
   return render_template("index.html")

def getLangquery(lang):
    lang=lang.lower()
    l=lang.replace(',',"','")
    q="'"
    q+=l
    q+="'"
    return q

def getTopicsquery(topic):
    topic = topic.lower()
    topics = topic.split(',')
    q="("
    tempq=""
    for t in topics:
        tempq+="LOWER(subject) like ('%s%%') OR LOWER(bookshelf) like ('%s%%')"%(t,t)
        tempq+=" OR "

    q+=tempq[:-3]
    q+=")"

    return q





@app.route('/filterBooks',methods=['GET','POST'])
def filterbooks():
    id=request.args['gutenberg_id']
    lang=request.args['langs']
    mime = request.args['mime']
    topics = request.args['topics']
    author = request.args['author']
    title = request.args['title']

    query="select id,title,author,dob,dod,genre,language_code,subject,bookshelf,url from allbooks"
    c=" where "

    if len(str(id))>0:
        query+=c
        c=" and "
        q="gutenberg_id = %s"%id
        query+=q

    if len(str(lang)) > 0:
        query += c
        c = " and "
        q = getLangquery(lang)
        q="LOWER(language_code) in (%s)"%q
        query += q
    if len(str(mime)) > 0:
        query += c
        c = " and "
        q = "LOWER(mime) = LOWER('%s')" %mime
        query += q
    if len(str(topics)) > 0:
        query += c
        c = " and "
        q=getTopicsquery(topics)
        query += q

    if len(str(author))>0:
        query+=c
        c=" and "
        q="LOWER(author) = LOWER('%s')"%author
        query+=q

    if len(str(title))>0:
        query+=c
        c=" and "
        q="LOWER(title) = LOWER('%s')"%title
        query+=q
    query+=' Order by download_count DESC NULLS LAST;'

    cur = conn.cursor()
    cur.execute(query)
    res=cur.fetchall()
    resultFinal=[]
    ids={}
    t=0
    ignore=[]
    for r in res:
        if r[0] in ids.keys():

            if r[-3] in ids[r[0]].keys():
                id=ids[r[0]][r[-3]]
                resultFinal[id][-1] +=' , '
                resultFinal[id][-1]+=r[-1]
            else:
                ids[r[0]][r[-3]]=t
                resultFinal.append(list(r[1]))
                t+=1
        else:
            ids[r[0]]={r[-3]:t}
            resultFinal.append(list(r[1:]))
            t+=1
    return jsonify(resultFinal[:])


if __name__ == '__main__':
   app.run()

