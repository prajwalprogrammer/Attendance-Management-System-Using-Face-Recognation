from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.templatetags.static import static
from django.conf import settings
from csv import DictReader
import csv

import cv2

import numpy as np
import face_recognition
import os
from datetime import datetime, date
# Create your views here.


def index(request):
    return render(request, 'index.html')


def signup(request):
    return render(request, 'signup.html')


def login(request):
    return render(request, 'login.html')


def sign_up(request):
    if request.method == "POST":
        name = request.POST['name']
        username = request.POST['username']
        classname = request.POST['gmail']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "sorry, Enrollment is taken")
            return redirect('/signup')

        else:
            user = User.objects.create_user(
                first_name=name, last_name=classname, username=username, password=password)
            user.save()
            messages.info(request, "user Created")
            return redirect('/login')
    else:
        return render(request, 'signup.html')


def signnin(request):
    if request.method == "POST":
        login_userName = request.POST['username']
        login_password = request.POST['password']
        user = auth.authenticate(
            username=login_userName, password=login_password)
        if user is not None:
            auth.login(request, user)
            messages.info(request, "user Logged in")
            return redirect('/profile')
        else:
            messages.error(request, "Unable to login")
            return redirect('/login')
    else:
        print('\n User failed1')
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, "logout successfull")
    return redirect('/')


def profile(request):
    if request.user.is_authenticated:
        path = settings.MEDIA_ROOT
        img_list = os.listdir(path + '\Attendance')
        context = {'images': img_list}
        print(context)
        return render(request, "profile.html", context)

    else:
        return redirect('/login')


def addimage(request):

    cam = cv2.VideoCapture(0)
    directory = r'D:\CO6I\Face Recognation\account\media\Attendance'

    cv2.namedWindow("Python")
    os.chdir(directory)
    img_counter = 0

    while True:
        ret, freame = cam.read()
        if not ret:
            print("Failed")
            break
        cv2.imshow("Attendance", freame)

        k = cv2.waitKey(1)

        if k % 256 == 27:
            return HttpResponse("hiii")
            break
        elif k % 256 == 32:
            user = request.user.get_username()

            img_name = user+".jpg"
            cv2.imwrite(img_name, freame)
            print("Screen Taken")
            return redirect('/profile')
    cam.release()
    cam.destroyAllWindow()

    return HttpResponse("hiii")


def MarkAttendance(request):
    path = './media/Attendance'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)
    

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # print("image", img)
            try:
                encode = face_recognition.face_encodings(img)[0]
            except IndexError as e:
                print(e)

            encodeList.append(encode)
            # print(encodeList)
        return encodeList

    def markAttendance(name):
        queryset = User.objects.filter(
            username=name[:10]
        ).values('first_name', 'last_name')
        print(queryset[0]['first_name'])
        fullname = queryset[0]['first_name']
        classname = queryset[0]['last_name']
        with open('./Attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                today = date.today()
                Todaydate = today.strftime("%d / %m / %Y")

                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(
                    f'\n{name},{fullname},{classname},{Todaydate},{dtString}')

    # FOR CAPTURING SCREEN RATHER THAN WEBCAM
    # def captureScreen(bbox=(300,300,690+300,530+300)):
    #     capScr = np.array(ImageGrab.grab(bbox))
    #     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
    #     return capScr

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        #img = captureScreen()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(
                encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(
                encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2),
                              (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

        cv2.imshow('Webcam', img)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape Hit")
            break
    return redirect('/')


def desplayAttendance(request):
    with open('./Attendance.csv', 'r') as read_obj:
        read_file = csv.reader(read_obj)

        def fun(variable):
            letters = request.user.username
            if (variable[0] in letters):
                return True
            else:
                return False
        filtered = filter(fun, read_file)
        print(filtered)
        if request.user.is_staff:
            context = {'data': read_file}
        else:
            context = {'data': filtered}
        return render(request, 'attendance.html', context)


def aboutus(request):
    return render(request, 'aboutus.html')
