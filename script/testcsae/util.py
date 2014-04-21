Skip to content
 
This repository
Explore
Gist
Blog
Help
chengguopiao
 
 
1  Watch
Star 0 Fork 0PUBLICGuanjunXu/Social_New
 branch: master  Social_New / script / util.py 
GuanjunXu GuanjunXu 3 days ago Update util.py
1 contributor
 file  318 lines (272 sloc)  12.128 kb EditRawBlameHistory Delete
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
295
296
297
298
299
300
301
302
303
304
305
306
307
308
309
310
311
312
313
314
315
316
317
#!/usr/bin/python
# coding:utf-8

from devicewrapper.android import device as d
import commands
import re
import subprocess
import os
import string
import time
import sys

##################################################################################################################
ADB = 'adb'
ADB_SHELL = ADB + ' shell'
ADB_DEVICES = ADB + ' devices'
ANDROID_SERIAL='ANDROID_SERIAL'
##################################################################################################################

MODE_LIST_BUTTON    = 'com.intel.camera22:id/mode_button'
MODE_ID             ={'single':'com.intel.camera22:id/mode_wave_photo',
                      'smile':'com.intel.camera22:id/mode_wave_smile',
                      'hdr':'com.intel.camera22:id/mode_wave_hdr',
                      'video':'com.intel.camera22:id/mode_wave_video',
                      'burstfast':'com.intel.camera22:id/mode_wave_burst',
                      #'burstslow':'com.intel.camera22:id/mode_wave_burst',
                      'perfectshot':'com.intel.camera22:id/mode_wave_perfectshot',
                      'panorama':'com.intel.camera22:id/mode_wave_panorama'
                      }


RESULT              = r'^>\d<$'
HORI_LIST_BUTTON    = 'com.intel.camera22:id/hori_list_button'
FLASH_SETTING       = ['off','on','auto']


##################################################
#            Settings in each mode               #
##################################################
SINGLE_SETTING      = ['testcamera','hits','location','picturesize','scencesmode','exposure','whitebalance','iso','delay']
SMILE_SETTING       = ['location','picturesize','sencesmode','exposure','whitebalance','iso']
HDR_SETTING         = ['location','picturesize','delay']
VIDEO_SETTING       = ['testcamera','location','videosize','exposure','whitebalance']
BURST_SETTING       = ['location','picturesize','sencesmode','exposure']
PERFECTSHOT_SETTING = ['location','scencesmode','exposure']
PANORAMA_SETTING    = ['location','exposure','iso']
SINGLE_SETTING_FRONT= ['location']
VIDEO_SETTING_FRONT = ['location']


MODE = {'single':SINGLE_SETTING,
        'smile':SMILE_SETTING,
        'hdr':HDR_SETTING,
        'video':VIDEO_SETTING,
        'burst':BURST_SETTING,
        'perfectshot':PERFECTSHOT_SETTING,
        'panorama':PANORAMA_SETTING,
        'fsingle':SINGLE_SETTING_FRONT,
        'fvideo':VIDEO_SETTING_FRONT
        }


XML_CONFIRM_LIST = {'hits': 'pref_camera_hints_key',
                    'location': 'pref_camera_geo_location_key',
                    'picturesize': 'pref_camera_picture_size_key',
                    'scencesmode': 'pref_camera_scenemode_key',
                    'exposure': 'pref_camera_exposure_key',
                    'whitebalance': 'pref_camera_whitebalance_key',
                    'iso': 'pref_camera_iso_key',
                    'delay': 'pref_camera_delay_shooting_key',
                    'videosize': 'pref_video_quality_key'
                    }
#################################################################################################################
CPTUREBUTTON_RESOURCEID ='com.intel.camera22:id/shutter_button'
FRONTBACKBUTTON_DESCR = 'Front and back camera switch'
CPTUREPOINT='adb shell input swipe 363 1145 359 1045 '
DRAWUP_CAPTUREBUTTON='adb shell input swipe 363 1145 359 1045 '
DRAWDOWN_MENU='adb shell input swipe 530 6 523 22'


CAMERA_ID = 'adb shell cat /data/data/com.intel.camera22/shared_prefs/com.intel.camera22_preferences_0.xml | grep pref_camera_id_key'
#################################################################################################################

class Adb():

    def cmd(self,action,path,t_path=None):
        #export android serial
        if not os.environ.has_key(ANDROID_SERIAL):
            self._exportANDROID_SERIAL()
        #adb commands
        action1={
        'refresh':self._refreshMedia,
        'ls':self._getFileNumber,
        'cat':self._catFile,
        'launch':self._launchActivity,
        'rm':self._deleteFile,
        'pm':self._resetApp
        }
        action2=['pull','push']
        if action in action1:
            return action1.get(action)(path)
        elif action in action2:
            return self._pushpullFile(action,path,t_path)
        else:
            raise Exception('commands is unsupported,only support [push,pull,cat,refresh,ls,launch,rm] now')

    def _refreshMedia(self,path):
        p = self._shellcmd('am broadcast -a android.intent.action.MEDIA_MOUNTED -d file://' + path)
        out = p.stdout.read().strip()
        if 'result=0' in out:
            return True
        else:
            return False

    def _resetApp(self,path):
        p = self._shellcmd('pm clear ' + path)
        return p

    def _getFileNumber(self,path):
        p = self._shellcmd('ls ' + path + ' | wc -l')
        out = p.stdout.read().strip()
        return string.atoi(out)


    def _launchActivity(self,component):
        p = self._shellcmd('am start -n ' + component)
        return p

    def _catFile(self,path):
        p = self._shellcmd('cat ' + path)
        out = p.stdout.read().strip()
        return out

    def _deleteFile(self,path):
        p = self._shellcmd('rm -r  ' + path)
        p.wait()
        number = self._getFileNumber(path)
        if number == 0 :
            return True
        else:
            return False

    def _pushpullFile(self,action,path,t_path):
        beforeNO = self._getFileNumber(t_path)
        p = self._t_cmd(action + ' ' + path + ' ' + t_path)
        p.wait()
        afterNO = self._getFileNumber(t_path)
        if afterNO > beforeNO:
            return True
        else:
            return False

    def _exportANDROID_SERIAL(self):
        #get device number
        device_number = self._getDeviceNumber()
        #export ANDROID_SERIAL=xxxxxxxx
        os.environ[ANDROID_SERIAL] = device_number

    def _getDeviceNumber(self):
        #get device number, only support 1 device now
        #show all devices
        cmd = ADB_DEVICES
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        p.wait()
        out=p.stdout.read().strip()
        #out is 'List of devices attached /nRHBxxxxxxxx/t device'
        words_before = 'List of devices attached'
        word_after = 'device'
        #get device number through separate str(out)
        device_number = out[len(words_before):-len(word_after)].strip()
        if len(device_number) >= 15:
            raise Exception('more than 1 device connect,only suppport 1 device now')
        else:
            return device_number

    def _shellcmd(self,func):
        cmd = ADB_SHELL + ' ' + func
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    def _t_cmd(self,func):
        cmd = ADB + ' ' + func
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

class SetMode():
    
    def switchcamera(self,mode):
        d(resourceId = MODE_LIST_BUTTON).click.wait()
        if mode == 'burstslow':
            d(resourceId = MODE_ID[mode]).click.wait()
            d(text = 'SLOW'),click.wait()
        elif mode == 'burstfast':
            d(resourceId = MODE_ID[mode]).click.wait()
            d(text = 'FAST').click()          
        else:
            d(resourceId = MODE_ID[mode]).click.wait()


    def _setFlashMode(self,option):
        d(resourceId = 'com.intel.camera22:id/left_menus_flash_setting').click.wait()
        d(resourceId = 'com.intel.camera22:id/hori_list_button')[FLASH_SETTING.index(option)].click.wait()

    def _setFDFRMode(self,option):
        FDFRStatus = commands.getoutput('adb shell cat /data/data/com.intel.camera22/shared_prefs/com.intel.camera22_preferences_0.xml | grep pref_fdfr_key')
        if FDFRStatus.find(option) == -1:
            d(resourceId = 'com.intel.camera22:id/left_menus_face_tracking').click.wait()
        else:
            pass
            #print 'current status is fdfr ' + option

    def setCameraSetting(self,mode,sub_mode,option):
        '''
        This method is used to set camera to one mode, sub-mode, and do any operate of this sub-mode.
        7 = Max element count in screen.
        2 = Length of settings - Max screen count


        Please input index number as sub_mode, input index number of options as option
        Such as:
        setCameraSetting('single',3,2)
        'single' means mode
        3 means the index number of Location in sub_mode list
        2 means the index number of Location off option in options list
        '''
    
        settings = MODE[mode]
        #if sub_mode > 8:
            #return False
        if sub_mode == 'flash':
            self._setFlashMode(option)
        elif sub_mode == 'fdfr':
            self._setFDFRMode(option)
        else:
            d(resourceId = 'com.intel.camera22:id/left_menus_camera_setting').click.wait(timeout=2000)
            if sub_mode <= 7:
                d(resourceId = HORI_LIST_BUTTON)[sub_mode-1].click.wait()
                if len(settings) >= 7:
                    d(resourceId = HORI_LIST_BUTTON)[option+7-1].click.wait()
                else:
                    d(resourceId = HORI_LIST_BUTTON)[option+len(settings)-1].click.wait()
            else:
                d.swipe(680,180,100,180)
                d(resourceId = HORI_LIST_BUTTON)[sub_mode-2-1].click.wait()
                d(resourceId = HORI_LIST_BUTTON)[option+7-1].click.wait()
            #return True

class TouchButton():

    def takePicture(self,status):
        # capture single image
        def _singlecapture():
            d(resourceId = CPTUREBUTTON_RESOURCEID).click.wait()
        # capture smile image
        def _smilecapture():
            d(resourceId = CPTUREBUTTON_RESOURCEID).click.wait()
            time.sleep(2)
            d(resourceId = CPTUREBUTTON_RESOURCEID).click.wait()
        # capture single image by press 2s
        def _longclickcapture():
            commands.getoutput(DRAWUP_CAPTUREBUTTON + '2000')
            time.sleep(2) 
        #Dictionary
        takemode={
                  'single'   :_singlecapture,
                  'smile'    :_smilecapture,
                  'longclick':_longclickcapture
                  }    
        takemode[status]()
     
    def takePictureCustomTime(self,status): 
        # capture image by press Custom Time
        commands.getoutput(DRAWUP_CAPTUREBUTTON+ (status+'000'))



    def takeVideo(self,status,capturetimes=0):
        # Start record video
        d(resourceId = CPTUREBUTTON_RESOURCEID).click.wait() 
        for i in range(0,capturetimes):
            #Tap on the center of the screen to capture image during taking video
            d(resourceId = 'com.intel.camera22:id/camera_preview').click.wait()
        # Set recording time, every capturing during record video takes about 3s
        time.sleep(status - capturetimes*3 -2)
        # Stop record video
        d(resourceId = CPTUREBUTTON_RESOURCEID).click.wait() 
        return True


    def switchBackOrFrontCamera(self,status):
        # Dictionary
        camerastatus = {'back': '0','front':'1'}
        # Get the current camera status
        currentstatus = commands.getoutput(CAMERA_ID)
        # Confirm the current status of the user is required
        if currentstatus.find(camerastatus.get(status)) == -1:
            # draw down the menu
            commands.getoutput(DRAWDOWN_MENU)
            time.sleep(1)
            # set the camera status
            d(description = FRONTBACKBUTTON_DESCR).click.wait()
            time.sleep(3)
            # Get the current camera status
            currentstatus = commands.getoutput(CAMERA_ID)
            # check the result
            if currentstatus.find(camerastatus.get(status)) != -1:
                #print ('set camera is '+status)
                return True
            else:
                #print ('set camera is '+status+' fail')
                return False
        else:
            #print('Current camera is ' + status)
            pass

if __name__ == '__main__':
    a = Adb()
    a.cmd('pm','com.intel.camera22')
    print a.cmd('pm','com.intel.camera22')
 
Status API Training Shop Blog About © 2014 GitHub, Inc. Terms Privacy Security Contact