import configparser
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


# FUNCTIONS
def generateID(fileName):

    max = 0

    files = json.load(open(fileName))

    for x in files:
        tempID = int(x)

        if tempID > max:
            max = tempID

    max+=1
    return str(max)

def getCommentsAndFileName(pageNumber):

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


def getStartingPage():

    min = 5000
    for x in files:

        tempID = int(x)

        if tempID < min:
            
            min = tempID


    return min


def getMaxPageNumber():
     max = 0

     for x in files:

         tempID = int(x)

         if tempID > max:
             max = tempID

     return max


# ROUTES
@app.route('/')
def root():
    if not session.get('logged_in'):
        print("you are not logged in")
        login = False
    else:
        print("you are logged in")
        login = True

    
    return render_template('index.html', login = login, background = url_for('static', filename = 'images/wucover3X.jpg'))


@app.route('/artists/')
def meettheclan():

    artists = data['Artists']

    returnArtists = []
    returnArtist = {}

    for x in artists:
        artist = artists[x]

        returnArtist = {"name": artist.get('name'),
        "genre": artist.get('genre'), "clanPhoto" : artist.get('clanPhoto'),
        "clanDescription" : artist.get('clanDescription'),
        "dateOfBirth": artist.get('dateOfBirth') }

        returnArtists.append(returnArtist)

    

    return render_template('meettheclan.html', background = url_for('static', filename = 'images/wucover3X.jpg'), artist = returnArtists, check = False)


@app.route('/albums/')
def albums():

        artists = data['Artists']

        returnAlbums = []

        for x in artists:
            artist = artists[x]

            for y in artist.get('albums'):

                
                returnAlbum = {"albumCover": y.get('albumCover'), "name" : y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength'),
                "albumDescription":y.get('albumDescription') }

                returnAlbums.append(returnAlbum)

        return render_template('meettheclan.html', background = url_for('static', filename = 'images/wucover3X.jpg'), albums = returnAlbums, check = True)


@app.route('/login', methods = ['POST', 'GET'])
def login():

    errors = []

    errorFlag = False

    if request.method == 'GET':
        return render_template('login.html')


    if request.method == 'POST':

       
        if request.form['password'] != "1234":
            error = {"passwordError": "Incorrect password"}
            errors.append(error)
            errorFlag = True

        if request.form['name'] != "admin":
            error = {"nameError": "Incorrect username"}
            errors.append(error)
            errorFlag = True

        if errorFlag == True:
            return render_template('login.html', errors = errors)

        if request.form['password'] ==  "1234" and request.form['name'] == "admin":
            session['logged_in'] = True

            return redirect('/')





    """

    if request.method == 'POST':

       
        if request.form['password'] != app.config['password']:
            error = {"passwordError": "Incorrect password"}
            errors.append(error)
            errorFlag = True

        if request.form['name'] != app.config['admin']:
            error = {"nameError": "Incorrect username"}
            errors.append(error)
            errorFlag = True

        if errorFlag == True:
            return render_template('login.html', errors = errors)

        if request.form['password'] ==  app.config['password'] and request.form['name'] == app.config['admin']:
            session['logged_in'] = True

            return redirect('/')
    """

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


        with open(session['currentFileName'], 'w') as outfile:

            json.dump(comments, outfile)

        return render_template('forum.html', comments = comments, pageNumber = session['pageNumber'], minPageNumber = session['minPageNumber'], maxPageNumber = session['maxPageNumber'], height = "100px")


@app.route('/deletePage', methods = ['POST'])
def deletePage():

    data = json.load(open(session['currentFileName']))

    fileName = session['currentFileName']

    pageNumber = session['pageNumber']


    if request.method == 'POST':

        for x in files:

            startingPage = getStartingPage()

            if pageNumber != startingPage:
                

                if x == str(pageNumber):
                 
                    
                    files.pop(x)
                    os.remove(fileName)
                    with open("data/files.json", 'w') as outfile:

                        json.dump(files, outfile)

                    break

        session['pageNumber'] = getStartingPage()

        minPageNumber  = session['pageNumber']

        maxPageNumber = getMaxPageNumber()

        pageNumber = session['pageNumber']

        session['minPageNumber'] = minPageNumber

        session['maxPageNumber'] = maxPageNumber

        data, session['currentFileName'] = getCommentsAndFileName(str(pageNumber))

        sortedComments = {}

        sortedComments = sortDictionary(data)

        return render_template('forum.html', comments = sortedComments, pageNumber = pageNumber, maxPageNumber = maxPageNumber, height = "100px", minPageNumber = minPageNumber)

@app.route('/nextPage', methods = ['POST'])
def nextPage():

    pageNumber = session['pageNumber']
    
    next = False

    if pageNumber != session['maxPageNumber']:

        for x in files:

            tempID = int(x)


            if next:
                print(tempID)
                break

            if tempID == pageNumber:
                next = True

        session['pageNumber'] = tempID    

        comments, session['currentFileName'] = getCommentsAndFileName(str(tempID))

        comments = sortDictionary(comments)

        return render_template('forum.html', comments = comments,  pageNumber = session['pageNumber'], maxPageNumber = session['maxPageNumber'], minPageNumber = session['minPageNumber'], height = "100px")


@app.route('/previoustPage', methods = ['POST'])
def previousPage():

    pageNumber = session['pageNumber']   

    tempPrev = 0
    tempID = 0

    if pageNumber != session['minPageNumber']:

        for x in files:
            
            tempPrev = tempID
            tempID = int(x)

            if tempID == pageNumber:
                tempID = tempPrev
                break
    
        session['pageNumber'] = tempID


    comments, session['currentFileName'] = getCommentsAndFileName(str(tempID))

    comments = sortDictionary(comments)
    
    return render_template('forum.html', comments = comments,  pageNumber = session['pageNumber'], maxPageNumber = session['maxPageNumber'], minPageNumber = session['minPageNumber'], height = "100px")


@app.route('/forumPost/', methods= ['POST'])
def forumPost():

    if request.method == 'POST':

        errors = []

        errorFlag = False

        name = request.form['name']

        message = request.form['message']
       
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
            return render_template('forum.html', errors = errors, comments = sortedComments,  pageNumber = session['pageNumber'], maxPageNumber = session['maxPageNumber'], 
            minPageNumber = session['minPageNumber']
            , height = "100px")

        today = str(date.today())

        comment = {
        generateID(currentFileName): { "name": name, "message": message, "date" : today
        }}

        if len(sortedComments) > 3:          

            id = generateID("data/files.json")

            today = today.replace('-', '')

            fileName = today + id
            file = {id : {"fileName" : fileName }}

            fileName = "data/" + fileName +".json"

            files.update(file)
            with open("data/files.json", 'w') as outfile:

                json.dump(files, outfile)

            with open(fileName, "w") as file:

                json.dump(comment, file)

            maxPageNumber = getMaxPageNumber()

            minPageNumber = getStartingPage()

            session['maxPageNumber'] = maxPageNumber

            session['minPageNumber'] = minPageNumber

            return render_template('forum.html', comments = sortedComments, pageNumber = session['pageNumber'],  maxPageNumber = session['maxPageNumber'], minPageNumber = session['minPageNumber'], height = "100px")


        else:

            sortedComments.update(comment)

            sortedComments = sortDictionary(sortedComments)

            with open(currentFileName, 'w') as outfile:

                json.dump(sortedComments, outfile)


            session['pageNumber'] = session['pageNumber']
        
            return render_template('forum.html', comments = sortedComments, pageNumber = session['pageNumber'], maxPageNumber = session['maxPageNumber'], minPageNumber = session['minPageNumber'], height = "100px")


@app.route('/forum/', methods=['GET'])
def forum():

    if request.method == 'GET':
     
            session['pageNumber'] = getStartingPage()

            minPageNumber  = session['pageNumber']

            maxPageNumber = getMaxPageNumber()

            pageNumber = session['pageNumber']

            session['minPageNumber'] = minPageNumber

            session['maxPageNumber'] = maxPageNumber

            data, session['currentFileName'] = getCommentsAndFileName(str(pageNumber))

            sortedComments = {}

            sortedComments = sortDictionary(data)

            return render_template('forum.html', comments = sortedComments, pageNumber = pageNumber, maxPageNumber = maxPageNumber, height = "100px", minPageNumber = minPageNumber)


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
            "genre": artist.get('genre'), "clanPhoto" : artist.get('clanPhoto'),
            "clanDescription" : artist.get('clanDescription'),
            "dateOfBirth": artist.get('dateOfBirth'), 
            "artistBio" : artist.get('artistBio') }
            returnArtists.append(returnArtist)

            for y in artist.get('albums'):

                returnAlbum = {"albumCover": y.get('albumCover'), 
                "name" : y.get('name'),
                "artistName": y.get('artistName'),
                "releaseDate": y.get('releaseDate'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength'),
                "albumDescription" : y.get('albumDescription'),
                "albumBio" : y.get('albumBio')}

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
                "artistName" : y.get('artistName'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength'),
                "albumDescription" : y.get('albumDescription'),
                "albumBio" : y.get('albumBio')}

                returnAlbums.append(returnAlbum)
                break


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

        #check to see if user typed artist name, date of birth, and genre
        if searchItem1.lower() == x or searchItem1 == artist.get('dateOfBirth') or searchItem1 == artist.get('genre'):

            if searchItem2 == 'Albums' or 'albums':

                for y in artist.get('albums'):
                    returnAlbum = {"name" : y.get('name'),
                    "albumCover" : y.get('albumCover'),
                    "releaseDate": y.get('releaseDate'),
                    "executiveProducer": y.get('executiveProducer'),
                    "albumLength": y.get('albumLength'),
                    "albumDescription": y.get('albumDescription') }

                    returnAlbums.append(returnAlbum)


                #returnArtists.append(returnArtist)
    return render_template('showResults.html', artist = returnArtists, albums = returnAlbums, height = "100px")


@app.route('/searchPost/', methods = ['POST'])
def searchPost():

    if request.method == 'POST':

        search = request.form['search']

        returnArtists = []
        returnAlbums = []

        #First we check if it is an artist name or date of birth or genre

        artists = data['Artists']

        for x in artists:
            artist = artists[x]

            getAlbums = artist.get('albums')

            found = False

            #check to see if user typed artist name, date of birth, and genre
            if search.lower() == x or search == artist.get('dateOfBirth') or search == artist.get('genre'):

                returnArtist = {"name": artist.get('name'),
                "genre": artist.get('genre'),
                "clanPhoto" : artist.get('clanPhoto'),
                "clanDescription" : artist.get('clanDescription'),
                "dateOfBirth": artist.get('dateOfBirth') }

                for y in getAlbums:

                    returnAlbum = {"artistName": y.get('artistName'),
                    "name":y.get('name'),
                    "releaseDate": y.get('releaseDate'),
                    "albumCover" : y.get('albumCover'),
                    "executiveProducer": y.get('executiveProducer'),
                    "albumLength": y.get('albumLength'),
                    "albumDescription": y.get('albumDescription')}

                    returnAlbums.append(returnAlbum)

                returnArtists.append(returnArtist)
                found = True

        # If not above, then the person is trying to find something album related
            if found == False:

                for y in artist.get('albums'):


                    if search == y.get('name') or search == y.get('releaseDate') or search == y.get('executiveProducer') or search == y.get('albumLength'):

                        returnAlbum = {"name" : y.get('name'),
                        "releaseDate": y.get('releaseDate'),
                        "albumCover" : y.get('albumCover'),
                        "executiveProducer": y.get('executiveProducer'),
                        "albumLength": y.get('albumLength'),
                        "albumDescription": y.get('albumDescription') }

                        returnAlbums.append(returnAlbum)

        return  render_template('showResults.html', artist = returnArtists, albums = returnAlbums, height = "100px")


@app.route('/search/<search>')
def showSearch(search):

    returnArtists = []
    returnAlbums = []

    #First we check if it is an artist name or date of birth or genre

    artists = data['Artists']

    for x in artists:
        artist = artists[x]



        getAlbums = artist.get('albums')

        found = False



        #check to see if user typed artist name, date of birth, and genre
        if search.lower() == x or search == artist.get('dateOfBirth') or search == artist.get('genre'):

            returnArtist = {"name": artist.get('name'),
            "genre": artist.get('genre'),
            "clanPhoto" : artist.get('clanPhoto'),
            "clanDescription" : artist.get('clanDescription'),
            "dateOfBirth": artist.get('dateOfBirth') }




            for y in getAlbums:

                returnAlbum = {"artistName": y.get('artistName'),
                "name":y.get('name'),
                "releaseDate": y.get('releaseDate'),
                "albumCover" : y.get('albumCover'),
                "executiveProducer": y.get('executiveProducer'),
                "albumLength": y.get('albumLength'),
                "albumDescription": y.get('albumDescription')}

                returnAlbums.append(returnAlbum)

            returnArtists.append(returnArtist)
            found = True


    # If not above, then the person is trying to find something album related
        if found == False:

            for y in artist.get('albums'):


                if search == y.get('name') or search == y.get('releaseDate') or search == y.get('executiveProducer') or search == y.get('albumLength'):

                    returnAlbum = {"name" : y.get('name'),
                    "releaseDate": y.get('releaseDate'),
                    "albumCover" : y.get('albumCover'),
                    "executiveProducer": y.get('executiveProducer'),
                    "albumLength": y.get('albumLength'),
                    "albumDescription": y.get('albumDescription') }

                    returnAlbums.append(returnAlbum)

    return  render_template('showResults.html', artist = returnArtists, albums = returnAlbums, height = "100px")


@app.errorhandler(404)
def error(error):
    return render_template('error.html')
    

def init(app):
    config = configparser.ConfigParser()
    try:
        config_location = "etc/defaults.cfg"
        config.read(config_location)

        app.config['DEBUG'] = config.get("config", "debug")
        app.config['ip_address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")
        app.config['admin'] = config.get("config", "admin")
        app.config['password'] = config.get("config", "password")
    except:
        print(str.append("Could not read configs from: " + config_location))


if __name__ == '__main__':
    init(app)
    app.run(
    host = app.config['ip_address'],
    port = int(app.config['port']))
