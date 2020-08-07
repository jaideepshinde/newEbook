
from flask import Flask,request,jsonify,render_template,url_for
app = Flask(__name__)
import psycopg2

import urllib.parse # for python 3+ use: from urllib.parse import urlparse
result = urllib.parse.urlparse("postgres://lsubjogtkaacze:cd58ddcfb5a7ad245fabc4530cf10779e45b769794248a0c32b2d9ede2d9c091@ec2-54-243-67-199.compute-1.amazonaws.com:5432/d9i62jfeqhrt1v")
# also in python 3+ use: urlparse("YourUrl") not urlparse.urlparse("YourUrl")
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname

conn = psycopg2.connect(dbname=database,user=username,password=password,host=hostname)

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
                resultFinal.append(list(r[1:]))
                t+=1
        else:
            ids[r[0]]={r[-3]:t}
            resultFinal.append(list(r[1:]))
            t+=1
    return jsonify(resultFinal[:])


if __name__ == '__main__':
   app.run(host="https://ebook-jd.herokuapp.com/")

