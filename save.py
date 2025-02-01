#Save Content
#pip install telethon (other modules is built-in)
from telethon import TelegramClient, events
import shutil
import time
from datetime import datetime
import os
import re

api_id = 'api id'
api_hash = 'api hash'
phone = 'phone number with +'
#starting your client
client = TelegramClient('love_you_cutie', api_id, api_hash).start(phone=phone)

#i will not explain this function as long it's so clear
@client.on(events.NewMessage(pattern='/test'))
async def ping_handler(event):
    me = await client.get_me()
    if event.sender_id != me.id:
       return
    else:
       await event.reply(f"i'm still working bro...")

#download all media in channel by invite link or channel id or username
@client.on(events.NewMessage(pattern='/all (.+)'))    
async def download_media(event):
    try:
        #get your id from session
        me = await client.get_me()
        #message url
        url = event.pattern_match.group(1).replace('https://t.me/', '') if 'https://t.me/+' not in event.pattern_match.group(1) else (re.search(r'https://t\.me/c/(\d+)/\d+', event.pattern_match.group(1)).group(1) if re.search(r'https://t\.me/c/(\d+)/\d+', event.pattern_match.group(1)) else event.pattern_match.group(1))
        #get channel info
        print(url)
        info = await client.get_entity(url)
        #channel id
        channel_id = info.id
        #download path
        download_path = f"private_content\\{channel_id}"
        #if download path not created
        if not os.path.exists(download_path):
            #create it
            os.makedirs(download_path)
        #the start message
        start_message = await event.reply(f'info about {channel_id}:\nname: {info.title}\nid: {channel_id}\n\ndownload from channel {info.title} started')
        #for every message in channel or group
        async for message in client.iter_messages(channel_id, limit=None):
            #download it if it's media (pic, vid, doc (anything except text messages))
            if message.media:
                #download media and save it to file path
                file_path = await client.download_media(message.media, download_path)
                #editing the message with downloaded file path
                await start_message.edit(f"file downloaded {file_path}")
                try:
                    #sending file to telegram
                    await client.send_file(me.id, f"{file_path}", caption=f"file {download_path} downloaded and sent at {datetime.now()}")
                    #delete file after sending
                    os.remove(file_path)
                except Exception as e:
                    #if error happens send it
                    await event.reply(f"Error: {e}")
            else:
                #save all channel messages to txt file
                file = f'{download_path}{channel_id}.txt'
                with open(file, 'a') as f:
                    f.write(str(message.text)+'\n')
        #send the file
        await client.send_file(me.id, f"{file}", caption=f"file {file} downloaded and sent to {me.first_name} at {datetime.now()}")
        #delete the file
        os.remove(file)
    except Exception as e:
        #if error happens send it
        await event.reply(f"Error: {e}")
        
#download specific media in channel
@client.on(events.NewMessage(pattern='/down (.+)'))    
async def download_media(event):
    try:
        #get your id from session
        me = await client.get_me()
        #message url
        url = (re.search(r'https://t\.me/([^/]+)/\d+', event.pattern_match.group(1))) if 'https://t.me/c/' not in event.pattern_match.group(1) else (re.search(r'https://t\.me/c/(\d+)/\d+', event.pattern_match.group(1))).group(1)
        #get channel info
        info = await client.get_entity(int(url) if url.isdigit() else str(url.group(1)))
        #channel id
        channel_id = info.id
        #get the message id from link
        match = re.search(r'/(\d+)$', event.pattern_match.group(1))
        #if message id found
        if match:
           #save message id to cute var like you :3
           message_id = match.group(1)
        #download path
        download_path = f"private_content\\{channel_id}"
        #if download path not created
        if not os.path.exists(download_path):
            #create it
            os.makedirs(download_path)
        #the start message
        start_message = await event.reply(f'info about {channel_id}:\nname: {info.title}\nid: {channel_id}\n\ndownload from channel {info.title} started')
        #download specific message in channel or group
        message = await client.get_messages(channel_id, ids=int(message_id))
        #download it if it's media (pic, vid, doc (anything except text messages))
        if message.media:
            #download media and save it to file path
            file_path = await client.download_media(message.media, download_path)
            #editing the message with downloaded file path
            await start_message.edit(f"file downloaded {file_path}")
            try:
                #sending file to telegram
                await client.send_file(me.id, file=file_path, caption=f"file {download_path} downloaded and sent at {datetime.now()}")
                #delete file after sending
                os.remove(file_path)
            except Exception as e:
                #if error happens send it
                await event.reply(f"Error: {e}")
        else:
            #save all channel messages to txt file
            file = f'{download_path}{channel_id}.txt'
            with open(file, 'a') as f:
                f.write(str(message.text)+'\n')
        if not message.media:
           #send the file
           await client.send_file(me.id, f"{file}", caption=f"file {file} downloaded and sent to {me.first_name} at {datetime.now()}")
           #delete the file
           os.remove(file)
    except Exception as e:
        #if error happens send it
        await event.reply(f"Error: {e}")

#function to download view once media        
@client.on(events.NewMessage(pattern='/get'))    
async def download_media(event):
    try:
        #get your id from session
        me = await client.get_me()
        #get replied message
        replied_message = await event.get_reply_message()
        #get the sender info from replied message object
        sender = await replied_message.get_sender()
        #get the sender id or username from sender object
        sender_info = sender.id if sender.username==None else sender.id
        #media download path
        download_path = f"private_content\\{sender_info}"
        #check if replied message is media
        if replied_message.media:
           #get the expire date of the file
           ttl_seconds = replied_message.media.ttl_seconds if replied_message.media else None
           #ignore it it's always None anyway :3
           ttl_period = replied_message.ttl_period if hasattr(replied_message, 'ttl_period') else None
           #download the message media
           file_path = await replied_message.download_media(file=download_path)
           #if ttl_seconds is lower than 31 then it have expire date
           if int(ttl_seconds) < 31 and ttl_period==None: 
               #send downloaded file to saved messages
               await client.send_file(me.id, f"{file_path}", caption=f"file {file_path} from {sender_info} downloaded and sent at {datetime.now()} btw the media will expire after {ttl_seconds} from open time")
            #if ttl_seconds is higher than 31 then it's view once
           elif int(ttl_seconds) > 31 and ttl_period==None:
               #send downloaded file to saved messages
               await client.send_file(me.id, f"{file_path}", caption=f"file {file_path} from {sender_info} downloaded and sent at {datetime.now()}")
           else:
               #it's not view once media :(
               await event.reply('reply to view once media with /get command to download it')
        else:
            #the message is text not media
            await event.reply('the message should be media')
    except Exception as e:
        #if error happens send it
        await event.reply(f"Error: {e}")             
           
           
with client:
    #run the code without stopping
    print('bot is running... hit https://github.com/iAayco/Save-Content-Userbot/ for any help or ask')
    client.run_until_disconnected()
