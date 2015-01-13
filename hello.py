import os
from flask import Flask, render_template, request, url_for
from pattern.en import tag
import sqlite3dbm
import itertools
import re
from math import fabs
app = Flask(__name__)
#app.config['SHELVE_FILENAME'] = 'word_result.shelve'
#init_app(app)
#word_complete =  get_shelve('c')
tag_table = {'adj.':'JJ' , 'det.':'DT' , 'n.':'NN' , 'v.':'VB.*' , 'prep.':'IN'}

def searchfun(lines):
    database = sqlite3dbm.sshelve.open('query_result.db')
    return_list = []
    try:
        for line in database[lines]:
            return_list.append(line)
    except Exception, e:
        pass
    return return_list

def search_all_index(lists , target):
    result = []
    for index ,word in enumerate(lists):
        if target == word:
            result.append(index)
    return result

def gdex(lists):
    dicts = sqlite3dbm.sshelve.open("gdex.db" , "r")
    Sent = sqlite3dbm.sshelve.open("Sents.db" , "r")
    result = []
    lists = lists.split(" ")[:-1]
    fin_set = set()
    flag = 1
    try:
        for word in lists:
            if flag:
                for sent_index in dicts[word]:
                    fin_set.add(sent_index)
                flag = 0
            else:
                temp_set = set()
                for sent_index in dicts[word]:
                    temp_set.add(sent_index)
                fin_set = fin_set & temp_set
        for sent_index in fin_set:
            Sent_list = Sent[str(sent_index)]
            begin_index = search_all_index(Sent_list , lists[0])
            for word in lists[1:]:
                next_index = search_all_index(Sent_list , word)
                cum_flag = False
                for i in begin_index:
                    for n in next_index:
                        if(int(fabs(i - n)) < 3):
                            cum_flag = True
                            break
                    if cum_flag:
                        break
                if not cum_flag:
                    break
                else:
                    begin_index = search_all_index(Sent_list , word)
            if cum_flag:
                return " ".join(Sent_list)
    except Exception, e:
        return ""
    return result 

def search_tag(pos_tag , content):
    tag_index = content.split(" ").index(pos_tag)
    temp = content.replace(pos_tag , '_')
    result = searchfun(temp)
    return_list = []
    for item in result:
        pos = str(tag(item)[tag_index][1])
        pattern = re.compile(tag_table[pos_tag])
        if pattern.match(pos):
            return_list.append(item)
    return return_list
def re_align(lists):
    database = sqlite3dbm.sshelve.open('query_result.db')
    result = []
    for statments in list(itertools.permutations(lists , len(lists))):
        statment =  " ".join(statments)
        try:
            if database[statment]:
                result.append(database[statment][0])
        except Exception, e:
            pass
    return result

def getkey(result):
    return int(result.split(" ")[-1])

def get_word(lists):
    return lists.split(" ")[0]

def word_re_align(words):
    word_complete = sqlite3dbm.sshelve.open('word_result.db' , 'r')
    result = []
    for word in itertools.permutations(words , len(words)):
        word =  "".join(word)
        try:
            if(get_word(word_complete[word][0]) == word):
                result.append(word_complete[word][0])
        except Exception, e:
            pass
    if not result:
        return ['Not Found!! 0']
    else:
        result = sorted(result , key = getkey , reverse=True)
        return result[0]

@app.route('/')
@app.route('/data')
def form(name=None):
    if not request.args.get('index'):
        index = '1'
    else:
        index = str(request.args.get('index'))
    if not request.args.get('k'):
        return render_template('test.html',  name='')
    lines = str(request.args.get('k'))
    result = []
    if '?' in lines:
        temp = lines.replace('?','')
        ans = [['False'], ['True']]
        if not searchfun(temp):
            return render_template('test.html',  name=ans[0], query = lines)
        else:
            return render_template('test.html',  name=ans[1], query = lines)
    



    if '|' in lines:
        lists = lines.split(" ")
        or_index = lists.index('|')
        replace_content = lists[or_index - 1]+' | '+lists[or_index + 1]
        temp = lines.replace(replace_content , lists[or_index - 1])
        result.extend(searchfun(temp))
        temp = lines.replace(replace_content , lists[or_index + 1])
        result.extend(searchfun(temp))
        result = sorted(result , key = getkey , reverse=True)
    if '_' in lines:
        result.extend(searchfun(lines))
    if '*' in lines:
        temp = lines.replace('*','_')
        result.extend(searchfun(temp))
        temp = lines.replace('*','_ _')
        result.extend(searchfun(temp))
        temp = lines.replace('*','_ _ _')
        result.extend(searchfun(temp))
        result = sorted(result , key = getkey , reverse=True)
    if 'adj.' in lines:
        result = search_tag('adj.' , lines)
    if 'det.' in lines:
        result = search_tag('det.' , lines)
    if 'n.' in lines:
        result = search_tag('n.' , lines)
    if 'v.' in lines:
        result = search_tag('v.' , lines)
    if 'prep.' in lines:
        result = search_tag('prep.' , lines)
    if 'r.' in lines:
        temp = lines.replace('r. ','')
        lists = temp.split(" ")
        result = re_align(lists)
    size = min(len(result),76)
    words = []
    numbers = []
    gdexs = []
    database = sqlite3dbm.sshelve.open('query_result.db')
    try:
        result = database[lines]
    except Exception, e:
        result = ["Not Found!!"]
    for item in result:
        gdexs.append(gdex(item))
        item =  item.split(" ")
        word = " ".join(item[:-1])
        number = item[-1]
        words.append(word)
        numbers.append(number)
    if size != 0:
        return render_template('test.html',index=index, name=result,gdex = gdexs, query = lines, size=size)
    return render_template('test.html',index=index, name=result,gdex = gdexs, query = lines, size=size)


def word_complete(lines):
    word_complete = sqlite3dbm.sshelve.open('word_result.db')
    try:
        if " " not in lines:
            return word_complete[lines][:10]
        elif " " == lines[-1] and "_" not in lines:
            word = lines.split(" ")[-2]
            try:
                word_complete[word]
            except Exception, e:
                return word_re_align(word)
            if not searchfun((lines + "_")):
                return ['Not Found!! 0']
            else:
                return searchfun((lines + "_"))[:10]
        else:
            prefix = " ".join(lines.split(" ")[:-1]) + " _"
            uncomplete = lines.split(" ")[-1]
            if uncomplete == "":
                return ['Not Found!! 0']
            reg = re.compile("^"+uncomplete)
            result = []
            for word in searchfun(prefix):
                if re.search(reg , word.split(" ")[-2]):
                    result.append(word)
            if not result:
                return ['Not Found!! 0']
            else:
                return result
    except Exception, e:
        return ['Not Found!! 0']


@app.route("/ajax_post_test", methods=['POST'])
def ajax_post_test():
    #if request.method == 'POST':
    #    print request.form["name"] + " " + request.form["city"]
    #    return "<p>Hello AJAX " + request.form["name"].upper() + " " + request.form["city"].upper() + " Test.</p>";
    hint_list = ''
    if request.form["value"] == '':
        return ''
    words = word_complete(request.form["value"])
    if type(words) == str:
        words = words.split(" ")[0]
        result = 'Do you query "<a href="?index=1&k='+ words +'">'+words+'?</a>'
    else:
        for word in words:
            word = ' '.join(word.split(' ')[:-1])
            hint_list += '<li><a href="?index=1&k='+ word +'">'+word+'</a></li>'
        result = '<ul>'+ hint_list + '</ul>'


    return result



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
