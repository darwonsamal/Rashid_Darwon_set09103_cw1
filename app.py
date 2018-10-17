import configparser
import Artist
import codecs
from flask import *
import json
from datetime import date
from operator import itemgetter
import os



app = Flask(__name__)
app.secret_key = os.urandom(12)

pageNumber = 0
currentFileName =""

data = json.load(open("data/data.json"))

files = json.load(open("data/files.json"))

@app.route('/')
def root():
    if not session.get('logged_in'):
        print("you are not logged in")
        login = False
    else:
        print("you are logged in")
        login = True
    return render_template('index.html', login = login, background = url_for('static', filename = 'images/wucover3X.jpg'))

@app.route('/meettheclan/')
def meettheclan():
    return render_template('meettheclan.html', background = url_for('static', filename = 'images/wucover3X.jpg'))

@app.route('/albums/')
def albums():
    print()


@app.route('/login', methods = ['POST', 'GET'])
def login():

    errors = []


    errorFlag = False

    if request.method == 'GET':
        return render_template('login.html')


    if request.method == 'POST':


        if request.form['password'] != '1234':
            error = {"passwordError": "Incorrect password"}
            errors.append(error)
            errorFlag = True

        if request.form['name'] != 'admin':
            error = {"nameError": "Incorrect username"}
            errors.append(error)
            errorFlag = True

        if errorFlag == True:
            return render_template('login.html', errors = errors)



        if request.form['password'] == '1234' and request.form['name'] == 'admin':
            session['logged_in'] = True

            return redirect('/')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/', code = 302)


@app.route('/delete/', methods=['POST'])
def deleteComment():

    data = json.load(open(session['currentFileName']))

    comments = data



    if request.method == 'POST':
        commentID = request.form.get('deleteComment')

        for i in comments:

            if i == commentID:

                comments.pop(i)
                break

        comments = sortDictionary(comments)


        with open(session['currentFileName'], 'w', encoding='utf8') as outfile:

            json.dump(comments, outfile)

        return render_template('forum.html', comments = comments, pageNumber = session['pageNumber'], maxPageNumber = len(files), height = "100px")



def generateID(fileName):

    max = 0

    files = json.load(open(fileName))

    for x in files:
        tempID = int(x)

        if tempID > max:
            max = tempID

    max+=1
    return str(max)


@app.route('/deletePage', methods = ['POST'])
def deletePage():

    data = json.load(open(session['currentFileName']))

    comments = data

    fileName = session['currentFileName']

    pageNumber = session['pageNumber']


    if request.method == 'POST':

        for x in files:

            if pageNumber != 1:
                print("entered")

                if x == str(pageNumber):
                    print("enetered   2222")
                    files.pop(x)
                    os.remove(fileName)
                    break


    return redirect('/forum')






@app.route('/nextPage', methods = ['POST'])
def nextPage():

    pageNumber = session['pageNumber']

    print(pageNumber)

    if pageNumber != len(files):


        pageNumber+=1

        session['pageNumber'] = pageNumber

        comments, session['fileName'] = getCommentsAndFileName(str(pageNumber))

        comments = sortDictionary(comments)

        return render_template('forum.html', comments = comments,  pageNumber = pageNumber, maxPageNumber = len(files))



@app.route('/previoustPage', methods = ['POST'])
def previousPage():

    pageNumber = session['pageNumber']

    print(pageNumber)

    if pageNumber > 1:

        pageNumber-=1

        session['pageNumber'] = pageNumber

        comments, session['fileName'] = getCommentsAndFileName(str(pageNumber))

        comments = sortDictionary(comments)

        return render_template('forum.html', comments = comments,  pageNumber = pageNumber, maxPageNumber = len(files))





def getCommentsAndFileName(pageNumber):

    tupleList = []

    for x in files:

        tempID = x


        if pageNumber == tempID:


            fileName = "data/" + files[x]['fileName'] + ".json"


            comments = json.load(open(fileName))

            return comments, fileName




def sortDictionary(comments):
    tupleList = []

    for x in comments:


        tempDate = int(comments[x]['date'].replace('-', ''))
        tempID = x


        tupleList.append((tempID, tempDate))



    tupleList = sorted(tupleList, key= itemgetter(1), reverse = True)

    sortedComments = {}
    for x in tupleList:

        for y in comments:

            if x[0] == y:

                comment = {y : { "name": comments[y]['name'], "message": comments[y]['message'], "date": comments[y]['date']}}


                sortedComments.update(comment)

    return sortedComments




@app.route('/forum/', methods=['POST', 'GET'])
def forum():

    errors = []

    errorFlag = False


    if request.method == 'POST':

            name = request.form['name']
            message = request.form['message']

            print(session['pageNumber'])

            data, session['currentFileName'] = getCommentsAndFileName(str(session['pageNumber']))

            currentFileName = session['currentFileName']

            sortedComments = {}

            sortedComments = sortDictionary(data)

            if name == "":
                error = {"nameError": "Please provide a name."}
                errors.append(error)
                errorFlag = True

            if message == "":
                error = {"messageError": "Please provide a message."}
                errors.append(error)
                errorFlag = True

            if errorFlag == True:
                return render_template('forum.html', errors = errors, comments = sortedComments,  pageNumber = session['pageNumber'], maxPageNumber = len(files)
                , height = "100px")

            today = str(date.today())



            comment = {
            generateID(currentFileName): { "name": name, "message": message, "date" : today
            }}



            if len(sortedComments) > 5:

                print("Entered")

                id = generateID("data/files.json")

                today = today.replace('-', '')

                fileName = today + id
                file = {id : {"fileName" : fileName }}

                fileName = "data/" + fileName +".json"

                files.update(file)
                with open("data/files.json", 'w', encoding='utf8') as outfile:

                    json.dump(files, outfile)

                with open(fileName, "w", encoding='utf8') as file:

                    json.dump(comment, file)

                return render_template('forum.html', comments = sortedComments, pageNumber = session['pageNumber'], maxPageNumber = len(files), height = "100px")



            else:

                sortedComments.update(comment)

                sortedComments = sortDictionary(sortedComments)

                with open(currentFileName, 'w', encoding='utf8') as outfile:

                    json.dump(sortedComments, outfile)

                return render_template('forum.html', comments = sortedComments, pageNumber = session['pageNumber'], maxPageNumber = len(files), height = "100px")

    else:

        session['pageNumber'] = 1

        pageNumber = session['pageNumber']

        data, session['currentFileName'] = getCommentsAndFileName(str(pageNumber))

        sortedComments = {}

        sortedComments = sortDictionary(data)

        print(len(files))


        return render_template('forum.html', comments = sortedComments, pageNumber = pageNumber, maxPageNumber = len(files), height = "100px")


@app.route('/artist/<artistName>')
def showArtist(artistName):
    artists = data['Artists']

    returnArtists = []
    returnAlbums = []
    returnArtist = {}

    for x in artists:
        artist = artists[x]

        if artistName.lower() == x:

            returnArtist = {"name": artist.get('name'),
            "genre": artist.get('genre'),
            "dateOfBirth": artist.get('dateOfBirth') }
            returnArtists.append(returnArtist)


            for y in artist.get('albums'):
                returnAlbum = {"albumCover": y.get('albumCover'), "name" : y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength') }

                returnAlbums.append(returnAlbum)


    return render_template('showArtist.html', artists = returnArtists, albums = returnAlbums, height = "100px")


@app.route('/album/<albumName>')
def showAlbum(albumName):
    artists = data['Artists']

    returnAlbums = []

    for x in artists:
        artist = artists[x]

        for y in artist.get('albums'):

            if y.get('name').lower() == albumName.lower():

                returnAlbum = {"albumCover": y.get('albumCover'), "name" : y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength') }

                returnAlbums.append(returnAlbum)


        return render_template('showAlbum.html', albums = returnAlbums, height = "100px")

    # check to see if it is either artist name or date of birth or genre
    # if variable check is true it means it is the above mentioned

@app.route('/<searchItem1>/<searchItem2>')
def showResults(searchItem1, searchItem2):
    artists = data['Artists']

    returnArtists = []
    returnAlbums = []

    for x in artists:
        artist = artists[x]

        getAlbums = artist.get('albums')

        #check to see if user typed artist name, date of birth, and genre
        if searchItem1.lower() == x or searchItem1 == artist.get('dateOfBirth') or searchItem1 == artist.get('genre'):

            if searchItem2 == 'Albums' or 'albums':

                for y in artist.get('albums'):
                    returnAlbum = {"name" : y.get('name'),
                    "releaseDate": y.get('releaseDate'),
                    "executiveProducer": y.get('executiveProducer'),
                    "albumLength": y.get('albumLength') }

                    returnAlbums.append(returnAlbum)


                #returnArtists.append(returnArtist)
    return render_template('showResults.html', artist = returnArtists, albums = returnAlbums, height = "100px")

@app.route('/search/<search>')
def showSearch(search):

    returnArtists = []
    returnAlbums = []

    check = True

    # check to see what search can bring up
    #for x in data:
    #    print(data[x]['GZA'].get('albums')[0]['artistName'])


        #print(data[x])
    #First we check if it is an artist name or date of birth or genre

    artists = data['Artists']

    for x in artists:
        artist = artists[x]



        getAlbums = artist.get('albums')






        #check to see if user typed artist name, date of birth, and genre
        if search.lower() == x or search == artist.get('dateOfBirth') or search == artist.get('genre'):

            returnArtist = {"name": artist.get('name'),
            "genre": artist.get('genre'),
            "dateOfBirth": artist.get('dateOfBirth') }




            for y in getAlbums:

                returnAlbum = {"artistName": y.get('artistName'),
                "name":y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength')}

                returnAlbums.append(returnAlbum)

            returnArtists.append(returnArtist)

    # If not above, then the person is trying to find something album related
        for y in artist.get('albums'):


            if search == y.get('name') or search == y.get('releaseDate') or search == y.get('executiveProducer') or search == y.get('albumLength'):

                returnAlbum = {"name" : y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength') }

                returnAlbums.append(returnAlbum)

    return  render_template('showResults.html', artist = returnArtists, albums = returnAlbums, height = "100px")




@app.route('/config')
def config():
    str = []
    str.append('Debug:' + app.config['DEBUG'])
    str.append('port:' + app.config['port'])
    str.append('url:' + app.config['url'])
    str.append('ip_address:' + app.config['ip_address'])

    return '\t'.join(str)

def init(app):
    config = configparser.ConfigParser()
    try:
        config_location = "etc/defaults.cfg"
        config.read(config_location)

        app.config['DEBUG'] = config.get("config", "debug")
        app.config['ip_address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")
    except:
        print(str.append("Could not read configs from: " + config_location))


if __name__ == '__main__':
    init(app)
    app.run(
    host = app.config['ip_address'],
    port = int(app.config['port']))
