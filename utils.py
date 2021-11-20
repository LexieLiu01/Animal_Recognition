# utils.py

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os.path
import urllib.parse
import json
import csv

PATH = './data'

### Basic checker
def check_url(url):
    ''' Check the accessiblility of the website
        @url: string. The target website link
        return nothing
        Print out the url, statue code of the request, the header returned, 
            and the encoding of the wesite.
    '''
    r = requests.get(url)
    # print("text: ",r.text)
    print("Checking url: %s" % url)
    print("Status code: ",r.status_code)
    print("Headers: ",r.headers)
    print("Encoding: ",r.encoding)
    # print("apparent_encoding: ",r.apparent_encoding)
    # print("content: ",r.content)


def soup_url(url, print_ = False):
    ''' Check the page content
        @url: string. The target website link
        @print_: boolean. False by default. If True, print out the prettified html.
        return the parased soup.
    '''
    r = requests.get(url)

    if r.status_code != 200:
        print("Status code %s on GET %s" % (str(r.status_code), url))

    html = r.text
    soup = BeautifulSoup(html,'lxml')

    if print_: 
        print(soup.prettify())

    return soup


def get_img(img_url):
    ''' GET image from url 
        @img_url: string. The targeted image link.
        return an image (Image object)
        If the retrival fails, it will print out the info and the url, and return None
    '''
    try:
        r = requests.get(img_url)   # GET request to the image link
        pil_img = Image.open(BytesIO(r.content)) # <class 'PIL.JpegImagePlugin.JpegImageFile'>
    except:
        print("Fail to get: " + img_url); # print out Exception message
        pil_img = None
    finally:
        return pil_img


def load_img(destination =None,filename = None):
    ''' Load image from file
        @destination: string. None by default. The full path to get the image file in directory.
        @filename: string. None by default. The name of the image. It will process to be 
            the destination of the image, e.g. destination = ./data/@filename.jpg 
        return an image (Image object)
    '''
    # Process the input to get the destination of the image
    if destination is None:
        if filename is None:
            print("Destination and filename is missing.")
            return
        else:
            destination = PATH + "/" + filename + ".jpg"
    
    # Open the image from destination and return it        
    try: 
        pil_img = Image.open(destination) ###
    except:
        print("Fail to open image file: " + destination)
        pil_img = None
    finally: 
        return pil_img


### Image Processing

def img_process(img): ### FLAG
    ''' Process the image
        @img: Image object.
        return Image object
    '''
    # im_array = np.asarray(pil_img) # <class 'numpy.ndarray'>
    return img


### Save

def save_img_as_jpg(img_url, filename = None, img_process_func = None):
    ''' Save image from url to file named "PATH/filename.jpg"
        @img_url: string. The link of the target image
        @filename: string. None by default. It use @img_url's "ixid" by default.
        @img_process_func: function. None by default.
        return image, and destination string
    '''
    if filename is None: # If the filename is not provided, it uses the url's "ixid" as id
        ''' Take ixid as filename 
        e.g. MnwxMjA3fDB8MHxzZWFyY2h8MXx8cGFuZGF8ZW58MHx8MHx8 '''
        filename = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(img_url).query))['ixid'] 
    
    if not os.path.exists(PATH): # If the PATH does not exit, create it.
        os.makedirs(PATH)
    
    destination = '%s/%s.jpg' % (PATH, filename) # the destination to save the jpg image.
    pil_img = get_img(img_url)  # Call the get_img() method to retrive image from url
    
    # If fails to retrive the image, it returns None, and empty destination string.
    if pil_img is None: 
        return pil_img, ""
    
    # Pre-cond: The image is retrived successfully 
    try: 
        if img_process_func is not None: # If iamge process function is provided, process it
            pil_img = img_process_func(pil_img) ### FLAG ###
        
        # Save the processed image to "destination"
        pil_img.save(destination)

        # ### Alternative
        # with open('%s/%s.jpg'%(PATH, filename),'wb') as f:
        #     f.write(r.content)
        #     f.close()
    except IOError: 
        # Error in save the image, and print out the image link for futher investigation
        print("Image is retrived. Fail to write image to file " + img_url)
        
        # nothing is saved, destination string is empty
        destination = "" 
    finally:
        return pil_img, destination


def save_img_destinations(img_destinations = None, query="unknown"):
    ''' Save a list of image destination to PATH/@query.txt 
        @img_destinations: a List of string. e.g. ["img1.jpg", "img2.jpg", ...]. None by default. 
        @query: string. The filename to save the destination. "unknown" by default.
            It is recommend to use query keyword for the filename, as label of these image.
        return string. The destination of the text file
    ''' 
    if img_destinations is None:
        print("Empty image destinations. Nothing to save")
        return None

    destination = '%s/%s.txt'%(PATH, query) # destination of the save text file
    
    # Append mode to write information. It will create file if not exists.
    with open(destination,'a') as file: 
        for img_destination in img_destinations:
            file.write(img_destination + '\n') # an image destination each row

        file.close()

    print("Image destinations are saved in: %s" % destination)
    return destination


def save_img_dict(dictionary = None, filename = "unknown"):
    ''' Save a dictionary of image dictionary {id:url} as json to "PATH/filename.json" 
        @dictionary: dict. None by default.
        @filename: string. The filename to save the image dictionary. "unknown" by default.
            It is recommend to use query keyword for the filename, as label of these image.
        return string. The destination of the json file
    '''
    if dictionary is None: 
        print("Empty image dictionary. Nothing to save")
        return None
        
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    destination = '%s/%s.json'%(PATH, filename) # destination of the save json file
    
    #Pre-cond: the dictionary exists
    try: 
        # Pre-cond: the json file already exist in the directory
        # for following update on the json file: read, update, write
        with open(destination, "r") as file:
            data = json.load(file)
            data.update(dictionary)
            file.close()

        with open(destination, "w") as file:
            json.dump(data, file)
            file.close()

        print("Image dictionary is saved in '%s' and total record %d." % (destination,len(data)))
    
    except FileNotFoundError: 
        # Creat the file for first saving
        with open(destination, "w") as file:
            json.dump(dictionary, file)
            file.close()
        print("Image dictionary is saved in '%s' and total record %d." % (destination,len(dictionary)))
    except:
        print("unknown error in save_img_dict")
        return "" # nothing have been saved

    return destination


def download_imgs_from_dict(img_dict):
    ''' Download the image  from url named by id, which is read from image dictionary
        @img_dict: dict. e.g.  {id1: url1, id2: url2, ...}. None by default.
        return nothing
    '''
    for id in img_dict.keys():
        # Use dictionary key (image id) as image filename, use value (image url) as url,
        # call save_img_as_jpg() to save imge from url.
        pil_img, destination = save_img_as_jpg(img_url = img_dict[id], filename = id, img_process_func = img_process)


def download_imgs_from_dict_file(img_dict_destination):
    ''' Download image from a dictionary which is read from image dictionary json.  
        @img_dict_destination: string. The string of the destionation of json file. e.g. PATH/query.json
        return nothing
    '''
    img_dict = load_img_dict(destination = img_dict_destination)
    download_imgs_from_dict(img_dict)

def download_imgs_from_urls(img_urls):
    ''' Download the image from url with default name
        @img_urls: a list of image url. e.g ["url1", "url2", ...] 
        return nothing
    '''
    for url in img_urls:
        # Use image url as url and named by default
        # call save_img_as_jpg() to save imge from url.
        pil_img, destination = save_img_as_jpg(img_url = url, img_process_func= img_process)

def save_annotations(queries = None, annotations_file = "unsplash.csv"):
    ''' Save the image annotation from .json files to a .csv file
        @queries: a list of string. e.g. ["str0, 'str1', ... ]
        return label_map = {"0": "str0", "1" : "str1",...}
    '''
    labels_map = dict()
    if queries:
        with open(annotations_file,'w',newline='') as csv_file:
            for label in range(len(queries)):
                class_dir = PATH + "/" + queries[label] + ".json"
                with open(class_dir,'r') as json_file:
                    data = json.load(json_file)
                    labels_map[str(label)] = queries[label]
                    for key in data:
                        csv_file.write(key + ".jpg, " + str(label) + ",\n")
        print("Records are saved to " + annotations_file)
    return labels_map
    
### Load 
def load_img_dict(destination = None, filename = None):
    ''' Load the image dictionary from json file
        @destination: string. The destionation of image dictionary. e.g. PATH/filename.json
        @filename: string. The filename of the image dictionary.
        return a dictionary from the file. None is returned if things go wrong
    '''
    if destination is None:
        if filename is None:
            print("Fail to load image dictionary, filename and destination are missing.")
            return dict()
        else:
            destination = '%s/%s.json'%(PATH, filename)
    try:
        with open(destination, "r") as file:
            img_dict = json.load(file)
    except FileNotFoundError:
        print("file does not exist!")
        img_dict = None
    except:
        print("Unknown error in load_img_dict")
        img_dict = None
        
    return img_dict

def load_imgs_from_dict_file(destination = None, filename = None):
    ''' Load image files, which names are stored in a json file
        @destination: string. The destination of json file.
        @filename: string. The filename of json file. Usually it is the query
        return a list of Image object
    '''
    # Load in the dictionary file
    img_dict = load_img_dict(destination = destination, filename = filename)
    imgs = [] # for storing images
    
    # Load image from file
    for img_name in img_dict.keys():
        # pre-processing the destination of the image
        img_destination = '%s/%s.jpg'%(PATH, img_name)
        # load image from destination
        pil_img = load_img(destination = img_destination) 
        # image could load failed.
        if pil_img is None:
            continue
        imgs.append(img_process(pil_img))
    return imgs
    
    
### Display
def show_img(img):
    ''' Show the image
        @img: Image object
    '''
    plt.imshow(img)
    plt.show()
        
def show_img_urls_in_group(img_urls, shape = None):
    """ Show all images from the image urls, and list into FIVE columns by default.
        @img_urls: list of image urls. e.g. ["url1","url2", ...]
        @shape: [int, int]. Shape of the image array. None by default.
    """
    if shape is None:
        shape = [len(img_urls)//5+1, 5]
    plt.figure()
    count = 1
    for img_url in img_urls:
        pil_img = get_img(img_url) # get the image from url
        if pil_img is None: 
            continue
        plt.subplot(shape[0],shape[1],count) # fill in the image array one by one
        plt.imshow(pil_img)
        plt.axis("off")
        count += 1

    plt.show()

def show_img_files_in_group(destinations = None, filenames = None, shape = None):
    """ Show all images from the image destinations, and list into FIVE columns
        @destinations: list of image destination.
        @filename: list of image filename.
        @shape: [int, int]. Shape of the image array. None by default.
    """
    prefix = ""
    postfix = ""
    if destinations is None: # pre-process of the image destination
        if filenames is None:
            print("Destinations and filenames are missing.")
            return
        else: # update the prefix and postfix for "destinations"
            prefix = PATH + "/"
            postfix = ".jpg"
            destinations = filenames
    else: # destination is not None       
        filenames = destinations
    
    if shape is None:
        shape = [len(filenames)//5+1, 5] # [#rows, #columns]
        
    plt.figure()
    count = 1
    for filename in filenames: 
        pil_img = load_img(destination = prefix + filename + postfix) # Load image from file
        if pil_img is None: 
            continue
        plt.subplot(shape[0],shape[1],count)
        plt.imshow(pil_img)
        plt.axis("off")
        count += 1

    plt.show()
