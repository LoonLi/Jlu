from flask import render_template,render_template_string,url_for,redirect,request
from app import app
import sys
reload(sys) 
sys.setdefaultencoding('utf8')
import search_for

@app.route("/", methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		context = request.form.get('context'," ")
		return redirect("/search/1/"+context)
	return render_template("index.html")

@app.route('/search/<int:page>/<context>', methods=['GET', 'POST'])
def search(page=1,context=""):
	if request.method == 'POST':
		return redirect("/search/1/"+request.form.get('context'," "))
	result = search_for.search_for(context)
	pages = {}
	page_count = len(result)/10 + 1
	if page < 1:
		page = 1
	if page > page_count:
		page = page_count
	if page_count > 5 and page > 4:
		if (page+2)>page_count:
			result_t = range(page_count-4,page_count+1)
		else:
			result_t = [x for x in range(page_count) if x > page-3 or x < page+3]
	else:
		result_t = range(1,page_count+1)
	pages['count'] = result_t
	pages['pre'] = page-1
	pages['next'] = page+1
	pages['page'] = page
	result = result[10*(page-1):10*page]
	return render_template("result.html",posts=result,pages=pages,context=context)