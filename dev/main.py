import base64

import googleapiclient.discovery
import googleapiclient.errors

import pytz
from datetime import datetime, timedelta

import pandas as pd

from os import getenv


def convert_utc_to_est(utc_timestamp):
  # parse the UTC timestamp into a datetime object
  utc_time = datetime.strptime(utc_timestamp, '%Y-%m-%dT%H:%M:%SZ')
  
  # create timezone objects for UTC and EST
  utc_zone = pytz.utc
  est_zone = pytz.timezone('US/Eastern')
  
  # convert the UTC datetime to EST datetime
  est_time = utc_zone.localize(utc_time).astimezone(est_zone)

  formatted_est_time = est_time.strftime('%A, %B %d, %Y: %I:%M %p EST')
  
  # format the EST datetime as a string in ISO format
  return est_time, formatted_est_time

def get_recent_weekend(est_time):
  # get the current time in EST timezone
  est_zone = pytz.timezone('US/Eastern')
  
  # calculate the start of the most recent weekend
  if est_time.weekday() == 5:  # it's currently Saturday
      start_time = datetime(est_time.year, est_time.month, est_time.day, 0, 0, 0, 0, est_zone)
  else:
      days_since_saturday = (est_time.weekday() + 1) % 7  # 0 = Saturday, 1 = Sunday, etc.
      start_time = est_time - timedelta(days=days_since_saturday+1, hours=est_time.hour, minutes=est_time.minute, seconds=est_time.second, microseconds=est_time.microsecond)
  
  # calculate the end of the most recent weekend
  end_time = start_time + timedelta(days=1, hours=23, minutes=59, seconds=59)
  
  # format the start and end times as strings
  start_time_str = start_time.strftime('%A, %B %d, %Y: %I:%M %p EST')
  end_time_str = end_time.strftime('%A, %B %d, %Y: %I:%M %p EST')
  print(start_time_str, end_time_str)
  
  return start_time, end_time


# get the latest videos from the most recent Saturday and Sunday
# Ideally, we are updating multiple times on Sunday morning

def get_youtube_videos(query: str):
  youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=getenv("API_KEY"))

  request = youtube.search().list(
      part="snippet",
      maxResults=25,
      order = "date",
      q=query
  )
  response = request.execute()

  # filter videos based on time; we want videos to fall in most recent weekend
  # we make exceptions for live videos and upcoming livestreams
  start_date, end_date = get_recent_weekend(est_time=datetime.now(pytz.timezone('US/Eastern')))
  res = dict()
  for vid in response["items"]:

      publish_time = vid["snippet"]["publishTime"]
      est_publish_time, formatted_est_publish_time = \
          convert_utc_to_est(utc_timestamp = publish_time)
      
      publish_time_in_window = (est_publish_time >= start_date) and (est_publish_time <= end_date)

      
      live_status = vid["snippet"]["liveBroadcastContent"]
      if live_status == "none":
          live_status = "completed"

      # we don't want videos that not live/upcoming and not in time window of recent weekend
      if live_status == "completed" and not publish_time_in_window:
          # print(live_status, formatted_est_publish_time, start_date, end_date)
          continue


      
      res[vid["id"]["videoId"]] = {
      "publish_time" : vid["snippet"]["publishTime"],
      "est_publish_time": est_publish_time,
      "formatted_est_publish_time": formatted_est_publish_time,
      "live_status": live_status,
      "title" : vid["snippet"]["title"],
      "channel_title" : vid["snippet"]["channelTitle"],
      "description" : vid["snippet"]["description"],
      "image_url": vid["snippet"]["thumbnails"]["high"]["url"],
      "video_url": "https://www.youtube.com/watch?v=" + vid["id"]["videoId"]
      }

  return res


def main():
  print("run main()")
  res1 = get_youtube_videos(query = "mar thoma church english holy communion")
  res2 = get_youtube_videos(query = "mar thoma church english holy qurbana")

  res2.update(res1)

  df = pd.DataFrame.from_dict(res2, orient='index')

  df = df.reset_index()
  df = df.rename(columns={'index': 'video_id'})
  df = df.sort_values(by="publish_time", ascending=False)
  # upload church services video
  df.to_csv("gs://gcf-sources-134756275535-us-central1/church/videos.csv", index=False)

  est_time = datetime.now(pytz.timezone('US/Eastern'))
  formatted_est_time = est_time.strftime('%A, %B %d, %Y: %I:%M %p EST')
  # upload update date
  pd.DataFrame([formatted_est_time], columns = ["update_date"]).to_csv("gs://gcf-sources-134756275535-us-central1/church/update_date.csv", index=False)
  return


# def hello_pubsub(event, context):
#   """Triggered from a message on a Cloud Pub/Sub topic.
#   Args:
#         event (dict): Event payload.
#         context (google.cloud.functions.Context): Metadata for the event.
#   """
#   pubsub_message = base64.b64decode(event['data']).decode('utf-8')
#   print(pubsub_message)
