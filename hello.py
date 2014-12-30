import os
from flask import Flask, render_template, request, url_for
from flask.ext.shelve import get_shelve, init_app

app = Flask(__name__)
app.config['SHELVE_FILENAME'] = 'word_result.shelve'
init_app(app)
word_complete =  get_shelve('c')

#word_complete = shelve.open('static/word_result.shelve' , 'r')

@app.route('/')
@app.route('/data')
def form(name=None):
	if not request.args.get('k'):
		return render_template('test.html',  name='')
	result = str(request.args.get('k'))
	if result:
		return render_template('test.html',  name=result)
	return render_template('test.html',  name='')

def word_complete(word):
    return word_complete[word]

@app.route("/ajax_post_test", methods=['POST'])
def ajax_post_test():
    #if request.method == 'POST':
    #    print request.form["name"] + " " + request.form["city"]
    #    return "<p>Hello AJAX " + request.form["name"].upper() + " " + request.form["city"].upper() + " Test.</p>";
    hint_list = ''
    if request.form["value"] == '':
	    return ''
    words = word_complete(request.form["value"])

    for word in words:
	    hint_list += '<li><a href="">'+word+'</a></li>'
    result = '<ul>'+ hint_list + '</ul>'
    return result

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
