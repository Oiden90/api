import os, flask
from flask import request, render_template, send_file
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')
	
@app.errorhandler(404)
def pageNotFound(e):
	return render_template('404.html')

#Used for wrapper to obtain video.
@app.route('/', methods=['POST'])
def getVideo():
	id = request.form['ytVideoID']
	startTime = request.form['startTime']
	endTime = request.form['endTime']
	
	queryUrl = 'https://www.youtube.com/embed/' 
	
	if id:
		queryUrl += '%s' % id
	if startTime:
		queryUrl += '?start=%s' % startTime
	if endTime:
		queryUrl += '&end=%s' % endTime
	if not (id or startTime or endTime):
		return pageNotFound(404)
	
	#modify youtube video
	queryUrl += '&controls=0&rel=0&autoplay=0&fs=0'
	
	#Obtain youtube video url and grab first .mp4 file by resolution and download
	yt = YouTube(queryUrl)
	yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()
	yt.download('./tmp/', filename='%s' % id)
	
	#ffmpeg used to crop the video at specific intervals
	ffmpeg_extract_subclip('./tmp/'+id+'.mp4', int(startTime), int(endTime), targetname='./tmp/cropped_'+id+'_'+startTime+'_'+endTime+'.mp4')
	
	return render_template('result.html', id=id, startTime=startTime, endTime=endTime, url=queryUrl)

#Used for url based api
@app.route('/api/v1/resources', methods=['GET'])
def apiFilter():
	queryParameters = request.args
	
	id = queryParameters.get('id')
	startTime = queryParameters.get('start')
	endTime = queryParameters.get('end')
	
	queryUrl = 'https://www.youtube.com/embed/'
		
	if id:
		queryUrl += '%s' % id
	if startTime:
		queryUrl += '?start=%s' % startTime
	if endTime:
		queryUrl += '&end=%s' % endTime
	if not (id or startTime or endTime):
		return pageNotFound(404)
	
	#modify youtube video
	queryUrl += '&controls=0&rel=0&autoplay=0&fs=0'
	
	#Obtain youtube video url and grab first .mp4 file by resolution and download
	yt = YouTube(queryUrl)
	yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()
	yt.download('./tmp/', filename='%s' % id)
	
	#ffmpeg used to crop the video at specific intervals
	ffmpeg_extract_subclip('./tmp/'+id+'.mp4', int(startTime), int(endTime), targetname='./tmp/cropped_'+id+'_'+startTime+'_'+endTime+'.mp4')
	
	return render_template('result.html', id=id, startTime=startTime, endTime=endTime, url=queryUrl)

#Used to specify file location for download
@app.route('/tmp/<videoID>\_<sTime>\_<eTime>')
def downloadFile(videoID,sTime,eTime):
	path = './tmp/cropped_'+videoID+'_'+sTime+'_'+eTime+'.mp4'
	
	return send_file(path)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)