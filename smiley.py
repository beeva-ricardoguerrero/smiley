import time, glob, requests, cv2, operator, random, datetime, up, filters, secrets, time, os
import numpy as np

colors = {'happiness': (0,255,0), 'sadness': (255,255,0), 'anger': (255,0,0)}
filters = filters.Filters()

def processRequest( json, data, headers, params ):
    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = secrets.OXFORD
    headers['Content-Type'] = 'application/octet-stream'

    retries = 0
    maxNumRetries = 10
    result = None
    while True:
        response = requests.request( 'post', 'https://api.projectoxford.ai/emotion/v1.0/recognize', json = json, data = data, headers = headers, params = params )
        if response.status_code == 429:
            print "Message: %s" % ( response.json()['error']['message'] )
            if retries <= maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print 'Error: failed after retrying!'
                break
        elif response.status_code == 200 or response.status_code == 201:
            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print "Error code: %d" % ( response.status_code )
            print "Message: %s" % ( response.json()['error']['message'] )
        break
    return result

def renderResultOnImage( result, img ):
    """Display the obtained results onto the input image"""

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        currEmotion = max(currFace['scores'].items(), key=operator.itemgetter(1))[0]

        textToWrite = "%s" % ( currEmotion )
        cv2.putText( img, textToWrite, (faceRectangle['left'],faceRectangle['top']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1 )

        faceRectangle = currFace['faceRectangle']
        colour = colors.get(currEmotion)
        if not colour:
            colour = (255,255,255)

        cv2.rectangle( img,(faceRectangle['left'],faceRectangle['top']),
                           (faceRectangle['left']+faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
                       color = colour, thickness = 5 )

def extractPortraits(picture, faces):
    portraits = []
    for face in faces:
        # Si tiene almendra o es un selfie ;)
        if float(face.get('faceRectangle').get('height')) / picture.shape[0] > 0.2:
            picHeight = face.get('faceRectangle').get('height') * 3
            picWidth = int(float(picHeight * 4) / 3)
            left = face.get('faceRectangle').get('left') - picWidth/3 + face.get('faceRectangle').get('width')/2
            top = face.get('faceRectangle').get('top') - picHeight/3 + face.get('faceRectangle').get('height')/3
        else:
            picHeight = face.get('faceRectangle').get('height') * 5
            picWidth = int(float(picHeight * 3) / 4)
            left = face.get('faceRectangle').get('left') - picWidth/2 + face.get('faceRectangle').get('width')/2
            top = face.get('faceRectangle').get('top') - picHeight/3 + face.get('faceRectangle').get('height')/3

        if left < 0:
            picWidth += left
            picHeight += left *  picWidth/picHeight
            left = 0
        if top < 0:
            picHeight += top
            picWidth += top * picHeight/picWidth
            top = 0

        #cv2.line(picture, (left, top + 2 * picHeight/3), (left + picWidth, top + 2 * picHeight/3), (255,255,255), thickness=1, lineType=8, shift=0)
        #cv2.line(picture, (left, top + picHeight/3), (left + picWidth, top + picHeight/3), (255,255,255), thickness=1, lineType=8, shift=0)

        #cv2.line(picture, (left + 2 * picWidth/3, top), (left + 2 * picWidth/3, top + picHeight), (255,255,255), thickness=1, lineType=8, shift=0)
        #cv2.line(picture, (left + picWidth/3, top), (left + picWidth/3, top + picHeight), (255,255,255), thickness=1, lineType=8, shift=0)

        crop_img = picture[top:top + picHeight, left:left + picWidth] # Crop from x, y, w, h -> 100, 200, 300, 400
        portraits.append(crop_img)
        # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]

        #cv2.rectangle( picture,(left, top), (left + picWidth, top + picHeight), color = colors.get('happiness'), thickness = 2 )
    return portraits

def extractLandscape(picture, faces):
    leftFace = min(faces, key = lambda x: x.get('faceRectangle').get('left'))
    left = leftFace.get('faceRectangle').get('left')
    rightFace = max(faces, key = lambda x: x.get('faceRectangle').get('left'))
    right = rightFace.get('faceRectangle').get('left') + rightFace.get('faceRectangle').get('width')
    topFace = min(faces, key = lambda x: x.get('faceRectangle').get('top'))
    top = topFace.get('faceRectangle').get('top')
    bottomFace = max(faces, key = lambda x: x.get('faceRectangle').get('top'))
    bottom = bottomFace.get('faceRectangle').get('top') + bottomFace.get('faceRectangle').get('height')

    #cv2.rectangle(picture,(left, top), (right, bottom), color = colors.get('happiness'), thickness = 2 )

    padding = picture.shape[0]/20 + picture.shape[0] / (bottom - top)

    height = float((right - left) * 9)/16

    upMultiplier = random.randint(1,2)
    downMultiplier = 1 if upMultiplier == 2 else 2

    top -= int(upMultiplier * height/3)
    if (top - padding) < 0:
        top = 0
        if padding > top:
            top = padding
    if (left - padding) < 0:
        left = 0
        if padding > left:
            left = padding
    bottom += int(downMultiplier * height/3)
    #cv2.rectangle(picture,(left - padding, top - padding), (right + padding, bottom + padding), color = colors.get('anger'), thickness = 2 )
    return [picture[top - padding: bottom + padding, left - padding: right + padding]]


def workWorkWorkWorkWork(picture, faces):
    smileyFaces = len(filter(lambda x: max(x.get('scores').items(), key=operator.itemgetter(1))[0] == 'happiness', faces))
    if smileyFaces <= 2:
        smileyPictures = extractPortraits(picture, faces)
    elif smileyFaces > 2:
        smileyPictures = extractLandscape(picture, faces)
    cv2.imshow("cropped", picture)
    cv2.waitKey(1)
    time.sleep(6)

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    # Encoding needed for the API
    encodedImage = cv2.imencode('.jpg', frame)[1].tostring()
    faces = processRequest( None, encodedImage, None, None )
    if faces is not None:
        smileyFaces = len(filter(lambda x: max(x.get('scores').items(), key=operator.itemgetter(1))[0] == 'happiness', faces)) + 1
        print 'faces {} and smiley faces {}'.format(len(faces), smileyFaces)
        if len(faces) > 0 and float(smileyFaces)/len(faces) > 0.66:
            smileyPictures = []
            if smileyFaces <= 2:
                smileyPictures = extractPortraits(frame, faces)
            elif smileyFaces > 2:
                smileyPictures = extractLandscape(frame, faces)
            for picture in smileyPictures:
                fileName = str(time.time()).replace('.','') + '.jpg'
                cv2.imwrite(fileName, filters.nashville(picture))
                up.uploadTo(fileName)
                os.remove(fileName)
    time.sleep(5)
