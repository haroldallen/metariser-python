from PIL import Image
from PIL.ExifTags import TAGS
 
# open the image
image = Image.open("C:/Users/every/Pictures/Photography/Edited/24-08-10/CarShowWithTristan-A04.jpg")
 
# extracting the exif metadata
exifdata = image.getexif()
 
# looping through all the tags present in exifdata
for tagid in exifdata:
     
    # getting the tag name instead of tag id
    tagname = TAGS.get(tagid, tagid)
 
    # passing the tagid to get its respective value
    value = exifdata.get(tagid)
   
    # printing the final result
    print(f"{tagname}: {value}")