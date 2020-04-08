import base64
import requests
import json
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO

# data = data_original[1:-1]

# data = [[50.80583, -0.427663], [50.805829, -0.427636], [50.805832, -0.427572], [50.805851, -0.427537], [50.805899, -0.427489], [50.805928, -0.427482]]

# data = [[10, -100], [15, -20], [20, 40], [20, 60], [15, 80], [15, 100]]

def normalise_data(data):
    data = data[1:-1]
    df = pd.DataFrame(data)
    # print(df)
    df_x, df_y = df[0], df[1]
    df_x_diff, df_y_diff = df_x.max()-df_x.min(), df_y.max()-df_y.min()

    if df_x_diff < df_y_diff:
        x_y_diff = df_x_diff / df_y_diff
        weight = (255-x_y_diff)/2
        norm_x = ((df_x-df_x.min())/(df_x.max()-df_x.min()))*255*x_y_diff
        norm_x = norm_x.add(weight)
        norm_y = ((df_y-df_y.min())/(df_y.max()-df_y.min()))*255
    else:
        x_y_diff = df_y_diff / df_x_diff
        weight = (255-x_y_diff)/2
        norm_x = ((df_x-df_x.min())/(df_x.max()-df_x.min()))*255
        norm_y = ((df_y-df_y.min())/(df_y.max()-df_y.min()))*255*x_y_diff
        norm_y = norm_y.add(weight)

    norm_df = pd.concat([norm_x,norm_y], axis=1)
    norm_data = norm_df.values.tolist()

    print(x_y_diff)

    # normalised_df = ((df-df.min())/(df.max()-df.min()))*255
    # normalised_data = normalised_df.values.tolist()
    
    return norm_data

def draw_route(data):
    img = Image.new('RGBA', (256, 256))
    draw_img = ImageDraw.Draw(img)
     
    for i in range(len(data)):
        j = i + 1
        x1 = data[i][0]
        y1 = data[i][1]
        try:
            x2 = data[j][0]
            y2 = data[j][1]
        except:
            x2 = data[i][0]
            y2 = data[i][1]
        draw_img.line((x1,y1,x2,y2), width=1, fill=(255,0,0,255))
             
    # img.save('my_png.png')

    img = img.rotate(90)
    # img.show()

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return(img_str)


api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'

def post_image_str(api_key, image_str):
    session = requests.Session()
    base_url = "https://api.imgbb.com/1/upload"
    payload = {
            "key": api_key,
            "image": image_str
        }
    res = requests.post(base_url, payload)

    image_url = res.json()['data']['url']

    return(image_url)

def post_image(api_key):
    session = requests.Session()
    with open("cat.png", "rb") as file:
        base_url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": base64.b64encode(file.read())
        }
        res = requests.post(base_url, payload)

    image_url = res.json()['data']['url']
    print(image_url)
    print(res.json())
    return(image_url)

# if __name__ == '__main__':
#     normalised_route = normalise_data(data)
#     my_image_string = draw_route(normalised_route)
#     my_image_url = post_image_str(api_key, my_image_string)
#     print(my_image_url)

